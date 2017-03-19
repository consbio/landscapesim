"""
    Serializers for consuming job submissions for running models and generating reports
"""
import json
from rest_framework import serializers
from landscapesim.models import Library, Project, Scenario, RunScenarioModel
from landscapesim.async.tasks import run_model
from landscapesim.serializers.imports import RunControlImport, OutputOptionImport, InitialConditionsNonSpatialImport, \
    InitialConditionsSpatialImport, DeterministicTransitionImport, TransitionImport, \
    InitialConditionsNonSpatialDistributionImport, TransitionTargetImport, TransitionMultiplierValueImport, \
    TransitionSizeDistributionImport, TransitionSizePrioritizationImport, StateAttributeValueImport, \
    TransitionAttributeValueImport, TransitionAttributeTargetImport


BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']

CONFIG_INPUTS = (('run_control', RunControlImport),
                 ('output_options', OutputOptionImport),
                 ('initial_conditions_nonspatial_settings', InitialConditionsNonSpatialImport),
                 ('initial_conditions_spatial_settings', InitialConditionsSpatialImport))

VALUE_INPUTS = (('deterministic_transitions', DeterministicTransitionImport),
                ('transitions', TransitionImport),
                ('initial_conditions_nonspatial_distributions', InitialConditionsNonSpatialDistributionImport),
                ('transition_targets', TransitionTargetImport),
                ('transition_multiplier_values', TransitionMultiplierValueImport),
                ('transition_size_distributions', TransitionSizeDistributionImport),
                ('transition_size_prioritizations', TransitionSizePrioritizationImport),
                ('state_attribute_values', StateAttributeValueImport),
                ('transition_attribute_values', TransitionAttributeValueImport),
                ('transition_attribute_targets', TransitionAttributeTargetImport))


class AsyncJobSerializerMixin(object):

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

    parent_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')
    result_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')

    class Meta:
        model = RunScenarioModel
        fields = ('uuid', 'created', 'status', 'inputs', 'outputs', 'parent_scenario', 'result_scenario')
        read_only_fields = ('uuid', 'created', 'status', 'outputs', 'parent_scenario', 'result_scenario')

    def validate_inputs(self, value):
        value = super(AsyncJobSerializerMixin).validate_inputs(value)
        if value:
            try:
                if all(x in value.keys() for x in CONFIG_INPUTS):
                    return value    # TODO - use the inner meta validated data to serialize the data
                else:
                    raise serializers.ValidationError('Missing one of {}'.format(CONFIG_INPUTS))
            except ValueError:
                raise serializers.ValidationError('Invalid configuration')
        return {}

    #def validate(self, attrs):

        # TODO - validate other inputs (transition probabilities, state/transition attributes, etc...)
        # This will be necessary to import other items if we want to run the new values
        # We don't need to add database rows into the system as those will be captured after a model run is complete
        # For now, it is enough that we can run scenarios as stock models

    #    return attrs

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
