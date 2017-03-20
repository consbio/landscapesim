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

# TODO - move this constant to ../config.py
CONFIG_IMPORTS = (('run_control', 'STSim_RunControl', config.RUN_CONTROL),
                  ('output_options', 'STSim_OutputOptions', config.OUTPUT_OPTION),
                  ('initial_conditions_nonspatial_settings', 'STSim_InitialConditionsNonSpatial', config.INITIAL_CONDITIONS_NON_SPATIAL),
                  #('initial_conditions_spatial_settings', 'STSim_InitialConditionsSpatial')
                  )

# TODO - move this constant to ../config.py
# Configuration of input data (probabilities, mappings, etc.)
VALUE_IMPORTS = (('deterministic_transitions', 'STSim_DeterministicTransition', config.DETERMINISTIC_TRANSITION),
                 ('transitions', 'STSim_Transition', config.TRANSITION),
                 ('initial_conditions_nonspatial_distributions', 'STSim_InitialConditionsNonSpatialDistribution',
                  config.INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION),
                 ('transition_targets', 'STSim_TransitionTarget', config.TRANSITION_TARGET),
                 ('transition_multiplier_values', 'STSim_TransitionMultiplierValue',
                  config.TRANSITION_MULTIPLIER_VALUE),
                 ('transition_size_distributions', 'STSim_TransitionSizeDistribution',
                  config.TRANSITION_SIZE_DISTRIBUTION),
                 ('transition_size_prioritizations', 'STSim_TransitionSizePrioritization',
                  config.TRANSITION_SIZE_PRIORITIZATION),
                 ('state_attribute_values', 'STSim_StateAttributeValue',
                  config.STATE_ATTRIBUTE_VALUE),
                 ('transition_attribute_values', 'STSim_TransitionAttributeValue',
                  config.TRANSITION_ATTRIBUTE_VALUE),
                 ('transition_attribute_targets', 'STSim_TransitionAttributeTarget',
                  config.TRANSITION_ATTRIBUTE_TARGET))


def import_configuration(console, config, sid, tmp_file):

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
