"""
    Model serializers for models that operate on a scenario basis, within a given project.
"""

from rest_framework import serializers

from landscapesim.models import \
    DistributionValue, RunControl, OutputOption, DeterministicTransition, Transition, InitialConditionsNonSpatial, \
    InitialConditionsNonSpatialDistribution, InitialConditionsSpatial, TransitionTarget, TransitionMultiplierValue, \
    TransitionSizeDistribution, TransitionSizePrioritization, TransitionSpatialMultiplier, StateAttributeValue, \
    TransitionAttributeValue, TransitionAttributeTarget

from landscapesim.serializers.custom import ScenarioInputServicesSerializer, ScenarioOutputServicesSerializer


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


class ScenarioConfigSerializer(serializers.Serializer):
    run_controls = RunControlSerializer(many=False, read_only=True)
    output_options = OutputOptionSerializer(many=False, read_only=True)
    initial_conditions_nonspatial_settings = InitialConditionsNonSpatialSerializer(many=False, read_only=True, allow_null=True)
    initial_conditions_spatial_settings = InitialConditionsSpatialSerializer(many=False, read_only=True, allow_null=True)
    scenario_input_services = ScenarioInputServicesSerializer(many=False, read_only=True)
    scenario_output_services = ScenarioOutputServicesSerializer(many=False, read_only=True)

    class Meta:
        fields = ('run_controls', 'output_options', 'initial_conditions_nonspatial_settings',
                  'initial_conditions_spatial_settings', 'scenario_input_services', 'scenario_output_services')
