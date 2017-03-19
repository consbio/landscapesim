"""
    Model serializers for models that operate on a scenario basis, within a given project.
"""

from rest_framework import serializers
from django.core.urlresolvers import reverse
from landscapesim.models import Scenario, \
    DistributionValue, RunControl, OutputOption, DeterministicTransition, Transition, InitialConditionsNonSpatial, \
    InitialConditionsNonSpatialDistribution, InitialConditionsSpatial, TransitionTarget, TransitionMultiplierValue, \
    TransitionSizeDistribution, TransitionSizePrioritization, TransitionSpatialMultiplier, StateAttributeValue, \
    TransitionAttributeValue, TransitionAttributeTarget, ScenarioInputServices, ScenarioOutputServices

class DistributionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionValue
        fields = '__all__'


class RunControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunControl
        fields = '__all__'


class OutputOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutputOption
        fields = '__all__'


class DeterministicTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeterministicTransition
        fields = '__all__'


class TransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transition
        fields = '__all__'


class InitialConditionsNonSpatialSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialConditionsNonSpatial
        fields = '__all__'


class InitialConditionsNonSpatialDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialConditionsNonSpatialDistribution
        fields = '__all__'


class InitialConditionsSpatialSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialConditionsSpatial
        fields = '__all__'


class TransitionTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionTarget
        fields = '__all__'


class TransitionMultiplierValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionMultiplierValue
        fields = '__all__'


class TransitionSizeDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionSizeDistribution
        fields = '__all__'


class TransitionSizePrioritizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionSizePrioritization
        fields = '__all__'


class TransitionSpatialMultiplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionSpatialMultiplier
        fields = '__all__'


class StateAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateAttributeValue
        fields = '__all__'


class TransitionAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionAttributeValue
        fields = '__all__'


class TransitionAttributeTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionAttributeTarget
        fields = '__all__'


class ScenarioValuesSerializer(serializers.Serializer):
    deterministic_transitions = DeterministicTransitionSerializer(many=True, read_only=True)
    transitions = TransitionSerializer(many=True, read_only=True)
    initial_conditions_nonspatial_distributions = InitialConditionsNonSpatialDistributionSerializer(many=True, read_only=True)
    transition_targets = TransitionTargetSerializer(many=True, read_only=True)
    transition_multiplier_values = TransitionMultiplierValueSerializer(many=True, read_only=True)
    transition_size_distributions = TransitionSizeDistributionSerializer(many=True, read_only=True)
    transition_size_prioritizations = TransitionSizePrioritizationSerializer(many=True, read_only=True)
    state_attribute_values = StateAttributeValueSerializer(many=True, read_only=True)
    transition_attribute_values = TransitionAttributeValueSerializer(many=True, read_only=True)
    transition_attribute_targets = TransitionAttributeTargetSerializer(many=True, read_only=True)

    class Meta:
        fields = ('deterministic_transitions', 'transitions', 'initial_conditions_nonspatial_distributions',
                  'transition_targets', 'transition_multiplier_values', 'transition_size_distributions',
                  'transition_size_prioritizations', 'state_attribute_values', 'transition_attribute_values',
                  'transition_attribute_targets')


class ScenarioInputServicesSerializer(serializers.ModelSerializer):

    stratum = serializers.SerializerMethodField(allow_null=True)
    secondary_stratum = serializers.SerializerMethodField(allow_null=True)
    stateclass = serializers.SerializerMethodField(allow_null=True)
    age = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = ScenarioInputServices
        fields = ('stratum', 'secondary_stratum', 'stateclass', 'age')

    def _get_url(self, service):
        return '/'.join(reverse('tiles_get_image', args=[service.name, 0, 0, 0])
                        .split('/')[:-3] + ['{z}', '{x}', '{y}.png'])

    def get_stratum(self, obj):
        if obj.stratum:
            return self._get_url(obj.stratum)
        else:
            return None

    def get_stateclass(self, obj):
        if obj.stateclass:
            return self._get_url(obj.stateclass)
        else:
            return None

    def get_secondary_stratum(self, obj):
        if obj.secondary_stratum:
            return self._get_url(obj.secondary_stratum)
        else:
            return None

    def get_age(self, obj):
        if obj.age:
            return self._get_url(obj.age)
        else:
            return None


class ScenarioOutputServicesSerializer(serializers.ModelSerializer):

    stateclass = serializers.SerializerMethodField(allow_null=True)
    transition_group = serializers.SerializerMethodField(allow_null=True)
    age = serializers.SerializerMethodField(allow_null=True)
    tst = serializers.SerializerMethodField(allow_null=True)
    stratum = serializers.SerializerMethodField(allow_null=True)
    state_attribute = serializers.SerializerMethodField(allow_null=True)
    transition_attribute = serializers.SerializerMethodField(allow_null=True)
    avg_annual_transition_group_probability = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = ScenarioOutputServices
        fields = ('stateclass', 'transition_group', 'age', 'tst',
                  'stratum', 'state_attribute', 'transition_attribute',
                  'avg_annual_transition_group_probability')

    def _get_url(self, service):
        variable_name = service.variable_set.first().name
        path_parts = reverse('timeseries_tiles_get_image', args=[
            service.name, variable_name, 0, 0, 0, 0]).split('/')[:-5]
        iteration_pattern = variable_name[:-len(variable_name.split('-')[-1])] + '{it}'
        return '/'.join(path_parts + [iteration_pattern, '{z}', '{x}', '{y}', '{t}.png'])

    def get_stateclass(self, obj):
        if obj.stateclass:
            return self._get_url(obj.stateclass)
        else:
            return None

    def get_transition_group(self, obj):
        if obj.transition_group:
            return self._get_url(obj.transition_group)
        else:
            return None

    def get_age(self, obj):
        if obj.age:
            return self._get_url(obj.age)
        else:
            return None

    def get_tst(self, obj):
        if obj.tst:
            return self._get_url(obj.tst)
        else:
            return None

    def get_stratum(self, obj):
        if obj.stratum:
            return self._get_url(obj.stratum)
        else:
            return None

    def get_state_attribute(self, obj):
        if obj.state_attribute:
            return self._get_url(obj.state_attribute)
        else:
            return None

    def get_transition_attribute(self, obj):
        if obj.transition_attribute:
            return self._get_url(obj.transition_attribute)
        else:
            return None

    def get_avg_annual_transition_group_probability(self, obj):
        if obj.avg_annual_transition_group_probability:
            return self._get_url(obj.avg_annual_transition_group_probability)
        else:
            return None


class ScenarioConfigSerializer(serializers.Serializer):
    run_control = RunControlSerializer(many=False, read_only=True)
    output_options = OutputOptionSerializer(many=False, read_only=True)
    initial_conditions_nonspatial_settings = InitialConditionsNonSpatialSerializer(many=False, read_only=True, allow_null=True)
    initial_conditions_spatial_settings = InitialConditionsSpatialSerializer(many=False, read_only=True, allow_null=True)
    scenario_input_services = ScenarioInputServicesSerializer(many=False, read_only=True)
    scenario_output_services = ScenarioOutputServicesSerializer(many=False, read_only=True)

    class Meta:
        fields = ('run_control', 'output_options', 'initial_conditions_nonspatial_settings',
                  'initial_conditions_spatial_settings', 'scenario_input_services', 'scenario_output_services')
