from celery.task import task
import json
import csv
from django.db import transaction
from landscapesim.models import Library, Scenario, RunScenarioModel
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.utils import get_random_csv, process_scenario_inputs
from landscapesim.io.reports import process_reports
from landscapesim.io.rasters import process_output_rasters
from landscapesim.io.config import CONFIG_IMPORTS, VALUE_IMPORTS
from django.conf import settings
exe = settings.STSIM_EXE_PATH


def import_configuration(console, config, sid, tmp_file):
    """
    Imports validated run configuration into csv formatted sheets for import.
    :param console: An instance of a landscapesim.io.consoles.STSimConsole
    :param config: Fully formatted dict object with validated data.
    :param sid: The scenario id which we are importing into.
    :param tmp_file: An absolute path to a csv file
    """

    print('Importing configuration for scenario {}'.format(sid))
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

    inputs = json.loads(job.inputs)
    import_configuration(console, inputs['config'], sid, get_random_csv(lib.tmp_file))

    try:
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")
    scenario_info = [x for x in console.list_scenario_attrs(results_only=True)
                     if int(x['sid']) == result_sid][0]

    with transaction.atomic():
        scenario = Scenario.objects.create(
            project=job.parent_scenario.project,
            name=scenario_info['name'],
            sid=result_sid,
            is_result=True
        )
        job.result_scenario = scenario
        job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
        job.save()

        process_scenario_inputs(console, scenario)
        process_reports(console, scenario, get_random_csv(lib.tmp_file))
        process_output_rasters(scenario)
