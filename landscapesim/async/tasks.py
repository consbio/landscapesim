from celery.task import task
import json
import csv
from django.db import transaction
from landscapesim.models import Library, Scenario, RunScenarioModel
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.utils import get_random_csv, process_scenario_inputs
from landscapesim.io.reports import process_reports
from landscapesim.io.rasters import process_output_rasters
from landscapesim.io import config
from django.conf import settings
exe = settings.STSIM_EXE_PATH


CONFIG_IMPORTS = (('run_control', 'STSim_RunControl', config.RUN_CONTROL),
                  ('output_options', 'STSim_OutputOptions', config.OUTPUT_OPTION),
                  ('initial_conditions_nonspatial_settings', 'STSim_InitialConditionsNonSpatial', config.INITIAL_CONDITIONS_NON_SPATIAL),
                  #('initial_conditions_spatial_settings', 'STSim_InitialConditionsSpatial')
                  )

# Configuration of input data (probabilities, mappings, etc.)
VALUE_IMPORTS = (('deterministic_transitions', 'STSim_DeterministicTransition'),
                 ('transitions', 'STSim_Transition'),
                 ('initial_conditions_nonspatial_distributions', 'STSim_InitialConditionsNonSpatialDistribution'),
                 ('transition_targets', 'STSim_TransitionTarget'),
                 ('transition_multiplier_values', 'STSim_TransitionMultiplierValue'),
                 ('transition_size_distributions', 'STSim_TransitionSizeDistribution'),
                 ('transition_size_prioritizations', 'STSim_TransitionSizePrioritization'),
                 ('state_attribute_values', 'STSim_StateAttributeValue'),
                 ('transition_attribute_values', 'STSim_TransitionAttributeValue'),
                 ('transition_attribute_targets', 'STSim_TransitionAttributeTarget'))


def import_configuration(console, config, sid, tmp_file):

    print('Importing configuration for scenario {}'.format(sid))
    for pair in CONFIG_IMPORTS:
        key = pair[0]
        sheet_name = pair[1]
        fieldnames = [x[1] for x in pair[2]]
        importable_data = config[key]
        with open(tmp_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(importable_data)
        print('Importing data for {}'.format(sheet_name))
        console.import_sheet(sheet_name, tmp_file, sid=sid, cleanup=True)

    # TODO - import value sheets
    print('Successfully import configuration for scenario {}'.format(sid))


@task(bind=True)
def run_model(self, library_name, pid, sid):
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
