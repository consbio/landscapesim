"""
    Serializers for consuming job submissions for running models and generating reports
"""
import json
import os
from rest_framework import serializers
from landscapesim.io.geojson import rasterize_geojson
from landscapesim.models import Library, Project, Scenario, RunScenarioModel, TransitionGroup
from landscapesim.async.tasks import run_model
from landscapesim.serializers.imports import RunControlImport, OutputOptionImport, InitialConditionsNonSpatialImport, \
    InitialConditionsSpatialImport, DeterministicTransitionImport, TransitionImport, \
    InitialConditionsNonSpatialDistributionImport, TransitionTargetImport, TransitionMultiplierValueImport, \
    TransitionSizeDistributionImport, TransitionSizePrioritizationImport, TransitionSpatialMultiplierImport, \
    StateAttributeValueImport, TransitionAttributeValueImport, TransitionAttributeTargetImport

# Need to know the library_name, and the inner project and scenario ids for any job
BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']

# Configuration flags for initialization
CONFIG_INPUTS = (('run_control', RunControlImport),
                 ('output_options', OutputOptionImport),
                 ('initial_conditions_nonspatial_settings', InitialConditionsNonSpatialImport),
                 #('initial_conditions_spatial_settings', InitialConditionsSpatialImport)
                 )

# Configuration of input data (probabilities, mappings, etc.)
VALUE_INPUTS = (('deterministic_transitions', DeterministicTransitionImport),
                ('transitions', TransitionImport),
                ('initial_conditions_nonspatial_distributions', InitialConditionsNonSpatialDistributionImport),
                ('transition_targets', TransitionTargetImport),
                ('transition_multiplier_values', TransitionMultiplierValueImport),
                ('transition_size_distributions', TransitionSizeDistributionImport),
                ('transition_size_prioritizations', TransitionSizePrioritizationImport),
                ('transition_spatial_multipliers', TransitionSpatialMultiplierImport),
                ('state_attribute_values', StateAttributeValueImport),
                ('transition_attribute_values', TransitionAttributeValueImport),
                ('transition_attribute_targets', TransitionAttributeTargetImport))


class AsyncJobSerializerMixin(object):
    """
        A base mixin for serializing the inputs and outputs, and validating that the minimum job info is provided.
    """

    status = serializers.CharField(read_only=True)
    inputs = serializers.JSONField(allow_null=True)
    outputs = serializers.JSONField(read_only=True)

    job_inputs = BASIC_JOB_INPUTS

    def validate_inputs(self, value):
        if value:
            try:
                value = json.loads(value)
                if all(x in value.keys() for x in self.job_inputs):
                    return value
                else:
                    raise serializers.ValidationError('Missing one of {}'.format(self.job_inputs))
            except ValueError:
                raise serializers.ValidationError('Invalid input JSON')

        return {}


class RunModelSerializer(AsyncJobSerializerMixin, serializers.ModelSerializer):
    """
        Main model run validation and transformation of data into importable info into SyncroSim.
    """

    parent_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')
    result_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')

    class Meta:
        model = RunScenarioModel
        fields = ('uuid', 'created', 'status', 'inputs', 'outputs', 'parent_scenario', 'result_scenario')
        read_only_fields = ('uuid', 'created', 'status', 'outputs', 'parent_scenario', 'result_scenario')

    @staticmethod
    def _filter_and_create_ics(config, library_name, pid, sid):
        return config   # Todo - create spatially-explicit initial conditions from special arguments (e.g. Landfire)

    @staticmethod
    def _filter_and_create_tsms(config, library_name, pid, sid):
        """ Takes a configuration, filters out geojson-specific data, and returns a valid configuration for import. """

        lib = Library.objects.get(name__exact=library_name)
        proj = Project.objects.get(library=lib, pid=pid)
        scenario = Scenario.objects.get(project=proj, sid=int(sid))
        is_spatial = scenario.run_control.is_spatial
        if is_spatial:
            if os.path.exists(scenario.multiplier_directory()):
                for file in os.listdir(scenario.multiplier_directory()):
                    os.remove(os.path.join(scenario.multiplier_directory(), file))

            # For each transition spatial multipler, create spatial multiplier files where needed
            for tsm in config['transition_spatial_multipliers']:
                tg = TransitionGroup.objects.get(id=tsm['transition_group']).name
                iterations = int(tsm['iteration']) if tsm['iteration'] is not None else 'all'
                timesteps = int(tsm['timestep']) if tsm['timestep'] is not None else 'all'
                tsm_file_name = "{tg}_{it}_{ts}.tif".format(tg=tg, it=iterations, ts=timesteps)
                tsm['transition_multiplier_file_name'] = tsm_file_name
                try:
                    geojson = tsm.pop('geojson')    # always remove the geojson entry
                    try:
                        rasterize_geojson(geojson,
                                          os.path.join(scenario.input_directory(),
                                                       scenario.initial_conditions_spatial_settings.
                                                       stratum_file_name),
                                          os.path.join(scenario.multiplier_directory(),
                                                       tsm_file_name))
                    except:
                        raise IOError("Error rasterizing geojson.")
                except KeyError:
                    print('{tg} multiplier did not have geojson attached, skipping...'.format(tg=tg))
        else:
            # We don't want to import any spatial multipliers, so filter out of configuration
            config['transition_spatial_multipliers'] = []
        return config

    def validate_inputs(self, value):
        value = super(RunModelSerializer, self).validate_inputs(value)
        if value:
            try:
                config = value['config']

                # At this stage we know these are valid and deserialized
                library_name = value['library_name']
                pid = value['pid']
                sid = value['sid']

                if all(x[0] in config.keys() for x in CONFIG_INPUTS + VALUE_INPUTS):

                    # Handle special filtering and file creation prior to model runs
                    config = self._filter_and_create_ics(config, library_name, pid, sid)
                    config = self._filter_and_create_tsms(config, library_name, pid, sid)

                    # Now validate pre-filtered deserialization
                    for pair in CONFIG_INPUTS + VALUE_INPUTS:
                        key = pair[0]
                        deserializer = pair[1]
                        config[key] = deserializer(config[key]).validated_data
                    value['config'] = config
                    return value
                else:
                    raise serializers.ValidationError('Missing one of {}. Got {}'.format(CONFIG_INPUTS, list(config.keys())))
            except ValueError:
                raise serializers.ValidationError('Invalid configuration')
        return {}

    def create(self, validated_data):

        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        lib = Library.objects.get(name__exact=library_name)
        proj = Project.objects.get(library=lib, pid=int(pid))
        parent_scenario = Scenario.objects.get(project=proj, sid=int(sid))
        result = run_model.delay(library_name, pid, sid)
        return RunScenarioModel.objects.create(
            parent_scenario=parent_scenario,
            celery_id=result.id,
            inputs=json.dumps(validated_data['inputs'])
        )
