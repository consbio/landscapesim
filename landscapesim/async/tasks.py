import csv
import json
import time

from celery.task import task
from django.conf import settings
from django.db import transaction

from landscapesim.io.config import CONFIG_IMPORTS, VALUE_IMPORTS
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.query import ssim_query
from landscapesim.io.rasters import process_output_rasters
from landscapesim.io.reports import process_reports
from landscapesim.io.utils import get_random_csv, process_run_control, process_scenario_inputs
from landscapesim.models import Library, Scenario, RunScenarioModel

exe = settings.STSIM_EXE_PATH


def import_configuration(console, config, sid, tmp_file):
    """
    Imports validated run configuration into csv formatted sheets for import.
    :param console: An instance of a landscapesim.io.consoles.STSimConsole
    :param config: Fully formatted dict object with validated data.
    :param sid: The scenario id which we are importing into.
    :param tmp_file: An absolute path to a csv file
    """

    print('Importing configuration for Scenario {}'.format(sid))
    for pair in CONFIG_IMPORTS + VALUE_IMPORTS:
        key = pair[0]
        sheet_name = pair[1]
        field_map = pair[2]
        fieldnames = [x[1] for x in field_map]
        importable_data = config[key]
        with open(tmp_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if pair in CONFIG_IMPORTS:
                writer.writerow(importable_data)
            else:
                for row in importable_data:
                    writer.writerow(row)
        print('Importing data for {}'.format(sheet_name))
        console.import_sheet(sheet_name, tmp_file, sid=sid, cleanup=True)
    print('Successfully imported run configuration for scenario {}'.format(sid))


def execute_ssim_queries(config, library, sid):
    # Currently no support for importing an empty table, but we need this here.
    if len(config.get('transition_spatial_multipliers')) == 0:
        ssim_query("DELETE FROM STSim_TransitionSpatialMultiplier WHERE ScenarioID={}".format(sid), library)



@task(bind=True)
def run_model(self, library_name, pid, sid):
    """
    Where all the magic happens. We perform a full import process into SyncroSim, let the model run complete, and then
    capture a snapshot of the library inputs and outputs and record them in our database. We also create all necessary
    input and output ncdjango services to provide map information.
    :param self: The celery task instance
    :param library_name: Unique name of the library containing the project.
    :param pid: The project id of the scenario (possibly unneeded)
    :param sid: The scenario id which we are running the model on. The scenario must not be a result scenario.
    """
    lib = Library.objects.get(name__iexact=library_name)
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    job = RunScenarioModel.objects.get(celery_id=self.request.id)
    job.model_status = 'starting'
    job.save()

    inputs = json.loads(job.inputs)
    t = time.time()
    import_configuration(console, inputs['config'], sid, get_random_csv(lib.tmp_file))
    execute_ssim_queries(inputs['config'], lib, sid)
    print("Import time: {}".format(time.time()- t))
    t = time.time()

    job.model_status = 'running'
    job.save()
    try:
        print('Running scenario {}...'.format(sid))
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")

    print("Model run time: {}".format(time.time() - t))

    scenario_info = [x for x in console.list_scenario_attrs(results_only=True)
                     if int(x['sid']) == result_sid][0]
    print('Model run complete - new scenario created: {}'.format(result_sid))
    with transaction.atomic():
        scenario = Scenario.objects.create(
            project=job.parent_scenario.project,
            name=scenario_info['name'],
            sid=result_sid,
            is_result=True
        )
        job.result_scenario = scenario
        job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
        job.model_status = 'processing'
        job.save()

    with transaction.atomic():
        t = time.time()
        process_run_control(console, scenario)
        process_output_rasters(scenario)
        print("Output rasters created in {} seconds".format(time.time() - t))
        t = time.time()
        process_reports(console, scenario, get_random_csv(lib.tmp_file))
        print("Reports created in {} seconds".format(time.time() - t))

        # Signal that the model can now be used for viewing.
        job.model_status = 'complete'
        job.save()

    # Post-processing for later usage
    with transaction.atomic():
        t = time.time()
        process_scenario_inputs(console, scenario)
        print("Scenario imported in {} seconds".format(time.time() - t))
