from celery.task import task
from landscapesim.models import Library, Scenario, RunScenarioModel
import json
import os
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.utils import get_random_csv, process_scenario_inputs
from landscapesim.io.reports import process_reports
from landscapesim.io.rasters import process_output_rasters
from django.conf import settings
exe = settings.STSIM_EXE_PATH


@task(bind=True)
def run_model(self, library_name, pid, sid):
    lib = Library.objects.get(name__iexact=library_name)
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    job = RunScenarioModel.objects.get(celery_id=self.request.id)

    inputs = json.loads(job.inputs)

    # TODO - extract, validate, and import related fields as necessary
    #        top-level nodes (i.e. 'transitions' should adhere to the API format we will need to declare

    try:
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")
    scenario_info = [x for x in console.list_scenario_attrs(results_only=True)
                     if int(x['sid']) == result_sid][0]
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
    tmp_file = get_random_csv(lib.tmp_file)
    process_reports(console, scenario, tmp_file)
    os.remove(tmp_file)
    process_output_rasters(scenario)
