import csv
import json
import time
import os
import re

from shutil import copyfile
from celery.task import task
from django.conf import settings

from landscapesim.io.config import CONFIG_IMPORTS, VALUE_IMPORTS
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.query import ssim_query
from landscapesim.io.rasters import process_output_rasters
from landscapesim.io.reports import ReportImporter
from landscapesim.io.utils import get_random_csv, process_run_control, process_scenario_inputs
from landscapesim.models import Library, Scenario, RunScenarioModel

EXE = getattr(settings, 'STSIM_EXE_PATH')
SCENARIO_SCAN_RATE = 2
DATASET_DOWNLOAD_DIR = getattr(settings, 'DATASET_DOWNLOAD_DIR')
STSIM_MULTIPLIER_DIR = getattr(settings, 'STSIM_MULTIPLIER_DIR')


def setup_transition_spatial_multipliers(config, parent):
    """
    If there are transition spatial multipliers, move them to the appropriate scenario location on disk.
    :param config:
    :param parent:
    """
    for tsm in config['transition_spatial_multipliers']:
        filename = tsm['MultiplierFileName']
        src = os.path.join(STSIM_MULTIPLIER_DIR, filename)
        dst = os.path.join(parent.multiplier_directory, filename)
        if not os.path.exists(parent.multiplier_directory):
            os.makedirs(parent.multiplier_directory)
        copyfile(src, dst)
        os.remove(src)      # Once the file is copied, we can cleanup the transition multipliers


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
def look_for_new_scenario(self, run_id):
    """ Scan for the new scenario that was created. """
    run = RunScenarioModel.objects.get(id=run_id)

    # If run is not spatial, return immediately
    is_spatial = json.loads(run.inputs)['config']['run_control']['IsSpatial']
    if not is_spatial:
        return

    recorded_sids = {x['sid'] for x in Scenario.objects.filter(is_result=True).values('sid')}
    spatial_directories = os.listdir(os.path.dirname(os.path.dirname(run.parent_scenario.output_directory)))
    directory_sids = {int(x.split('-')[1]) for x in spatial_directories}
    new_sids = directory_sids - recorded_sids
    if new_sids:
        sid = new_sids.pop()
        scenario, _ = Scenario.objects.get_or_create(
                    project=run.parent_scenario.project,
                    name=run.parent_scenario.name,
                    sid=sid,
                    is_result=True,
                    parent=run.parent_scenario
            )
        run.result_scenario = scenario
        run.save()
    else:
        time.sleep(SCENARIO_SCAN_RATE)
        look_for_new_scenario.delay(run_id)


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
    console = STSimConsole(exe=EXE, lib_path=lib.file, orig_lib_path=lib.orig_file)
    job = RunScenarioModel.objects.get(celery_id=self.request.id)
    parent = job.parent_scenario
    job.model_status = 'starting'
    job.save()

    inputs = json.loads(job.inputs)
    t = time.time()
    setup_transition_spatial_multipliers(inputs['config'], parent)
    import_configuration(console, inputs['config'], sid, get_random_csv(lib.tmp_file))
    execute_ssim_queries(inputs['config'], lib, sid)
    print("Import time: {}".format(time.time()- t))
    t = time.time()

    job.model_status = 'running'
    job.save()
    try:
        print('Running scenario {}...'.format(sid))
        look_for_new_scenario.delay(job.id)
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")
    print("Model run time: {}".format(time.time() - t))

    scenario_info = [x for x in console.list_scenario_attrs(results_only=True)
                     if int(x['sid']) == result_sid][0]
    print('Model run complete - new scenario created: {}'.format(result_sid))
    scenario, created = Scenario.objects.get_or_create(
        project=job.parent_scenario.project,
        name=scenario_info['name'],
        sid=result_sid,
        is_result=True,
        parent=job.parent_scenario
    )

    # If running spatially, we should have caught the scenario 
    if not created:
        job.refresh_from_db()
    else:
        job.result_scenario = scenario
    job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
    job.model_status = 'processing'
    job.save()

    t = time.time()
    process_run_control(console, scenario)
    process_output_rasters(scenario)
    print("Output rasters created in {} seconds".format(time.time() - t))
    t = time.time()
    reporter = ReportImporter(scenario, console)
    reporter.create_stateclass_summary()
    print("Reports created in {} seconds".format(time.time() - t))

        # Signal that the model can now be used for viewing.
    job.model_status = 'complete'
    job.save()

    # Start post-processing task for later usage and free worker.
    post_process_results.delay(job.id)


@task(bind=True)
def post_process_results(self, run_id):
    run = RunScenarioModel.objects.get(id=run_id)
    scenario = run.result_scenario
    lib = scenario.project.library
    console = STSimConsole(lib_path=lib.file, orig_path=lib.orig_file, exe=EXE)
    t = time.time()
    process_scenario_inputs(console, scenario, create_input_services=False)
    print("Scenario imported in {} seconds".format(time.time() - t))


@task
def cleanup_temp_files(age=7200):
    cutoff = time.time() - age
    t_files = os.listdir(DATASET_DOWNLOAD_DIR)
    for t_file in t_files:
        if re.search('.zip$', t_file):
            path = os.path.join(DATASET_DOWNLOAD_DIR, t_file)
            if os.path.getctime(path) < cutoff:
                try:
                    os.remove(path)
                except OSError:
                    pass
        if re.search('.pdf$', t_file):
            path = os.path.join(DATASET_DOWNLOAD_DIR, t_file)
            if os.path.getctime(path) < cutoff:
                try:
                    os.remove(path)
                except OSError:
                    pass
