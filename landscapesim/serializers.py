from rest_framework import serializers
from landscapesim.models import Library, Project, Scenario, Terminology, DistributionType, Stratum, SecondaryStratum,\
    StateClass, TransitionType, TransitionGroup, TransitionTypeGroup, TransitionMultiplierType, AttributeGroup, \
    StateAttributeType, TransitionAttributeType

from landscapesim.models import \
    DistributionValue, RunControl, OutputOption, DeterministicTransition, Transition, InitialConditionsNonSpatial, \
    InitialConditionsNonSpatialDistribution, InitialConditionsSpatial, TransitionTarget, TransitionMultiplierValue, \
    TransitionSizeDistribution, TransitionSizePrioritization, TransitionSpatialMultiplier, StateAttributeValue, \
    TransitionAttributeValue, TransitionAttributeTarget

from landscapesim.models import \
    StateClassSummaryReport, StateClassSummaryReportRow, \
    TransitionSummaryReport, TransitionSummaryReportRow, \
    TransitionByStateClassSummaryReport, TransitionByStateClassSummaryReportRow, \
    StateAttributeSummaryReport, StateAttributeSummaryReportRow, \
    TransitionAttributeSummaryReport, TransitionAttributeSummaryReportRow


class LibrarySerializer(serializers.ModelSerializer):

    projects = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='project-detail',
        )

    class Meta:
        model = Library
        fields = ('id', 'name', 'projects',)


class ProjectSerializer(serializers.ModelSerializer):

    scenarios = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='scenario-detail',
        )

    class Meta:
        model = Project
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='project-detail'
        )

    class Meta:
        model = Scenario
        fields = '__all__'


class TerminologySerializer(serializers.ModelSerializer):

    class Meta:
        model = Terminology
        fields = '__all__'


class DistributionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistributionType
        fields = '__all__'


class StratumSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = Stratum
        fields = '__all__'


class SecondaryStratumSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = SecondaryStratum
        fields = '__all__'


class StateClassSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = StateClass
        fields = '__all__'


class TransitionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionType
        fields = '__all__'


class TransitionGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionGroup
        fields = '__all__'


class TransitionTypeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionTypeGroup
        fields = '__all__'


class TransitionMultiplierTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionMultiplierType
        fields = '__all__'


class AttributeGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeGroup
        fields = '__all__'


class StateAttributeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StateAttributeType
        fields = '__all__'


class TransitionAttributeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionAttributeType
        fields = '__all__'


class ProjectDefinitionsSerializer(serializers.Serializer):
    """
        Special serializer for a one-stop-shop for collecting all
        project definitions in one location
    """

    terminology = TerminologySerializer(read_only=True, many=True)    # TODO - once we make this 1to1, set many=False
    stateclasses = StateClassSerializer(read_only=True, many=True)
    strata = StratumSerializer(many=True, read_only=True)
    transition_types = TransitionTypeSerializer(many=True, read_only=True)
    transition_groups = TransitionGroupSerializer(many=True, read_only=True)
    transition_type_groups = TransitionTypeGroupSerializer(many=True, read_only=True)
    transition_attribute_types = TransitionAttributeTypeSerializer(many=True, read_only=True)
    state_attribute_types = StateAttributeTypeSerializer(many=True, read_only=True)
    attribute_groups = AttributeGroupSerializer(many=True, read_only=True)

    class Meta:
        fields = (""""'terminology',""" 'stateclasses', 'strata', 'transition_types', 'transition_groups',
                  'transition_type_groups', 'transition_attribute_types', 'state_attribute_types',
                  'attribute_groups',)


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

    run_controls = RunControlSerializer(many=True, read_only=True)
    output_options = OutputOptionSerializer(many=True, read_only=True)
    initial_conditions_nonspatial_settings = InitialConditionsNonSpatialSerializer(many=True, read_only=True, allow_null=True)
    initial_conditions_spatial_settings = InitialConditionsSpatialSerializer(many=True, read_only=True, allow_null=True)
    # TODO - add scenario input map services to this serializer

    class Meta:
        fields = ('run_controls', 'output_options', 'initial_conditions_nonspatial_settings',
                  'initial_conditions_spatial_settings')

""" Report Serializers """


class StateClassSummaryReportRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = StateClassSummaryReportRow
        fields = '__all__'


class StateClassSummaryReportSerializer(serializers.ModelSerializer):

    results = StateClassSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = StateClassSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionSummaryReportRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionSummaryReportRow
        fields = '__all__'


class TransitionSummaryReportSerializer(serializers.ModelSerializer):

    results = TransitionSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = TransitionSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionByStateClassSummaryReportRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionByStateClassSummaryReportRow
        fields = '__all__'


class TransitionByStateClassSummaryReportSerializer(serializers.ModelSerializer):

    results = TransitionByStateClassSummaryReportRowSerializer(many=True, read_only=True)
    
    class Meta:
        model = TransitionByStateClassSummaryReport
        fields = ('id', 'scenario', 'results',)


class StateAttributeSummaryReportRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = StateAttributeSummaryReportRow
        fields = '__all__'


class StateAttributeSummaryReportSerializer(serializers.ModelSerializer):

    results = StateAttributeSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = StateAttributeSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionAttributeSummaryReportRowSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionAttributeSummaryReportRow
        fields = '__all__'


class TransitionAttributeSummaryReportSerializer(serializers.ModelSerializer):

    results = TransitionAttributeSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = TransitionAttributeSummaryReport
        fields = ('id', 'scenario', 'results',)


class QueryScenarioReportSerializer(serializers.ModelSerializer):
    """
        Convenient serializer for connecting to available reports for a given scenario
    """

    stateclass_summary_reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='stateclasssummaryreport-detail'
    )

    transition_summary_reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='transitionsummaryreport-detail'
    )

    transition_by_sc_summary_reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='transitionbystateclasssummaryreport-detail'
    )

    state_attribute_summary_reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='stateattributesummaryreport-detail'
    )

    transition_attribute_summary_reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='transitionattributesummaryreport-detail'
    )

    class Meta:
        model = Scenario
        fields = ('stateclass_summary_reports', 'transition_summary_reports', 'transition_by_sc_summary_reports',
                  'state_attribute_summary_reports', 'transition_attribute_summary_reports',)
