from rest_framework import serializers
from django_stsim.models import Library, Project, Scenario, Stratum, StateClass,\
    TransitionType, TransitionGroup, TransitionTypeGroup, Transition, \
    StateClassSummaryReport, StateClassSummaryReportRow, \
    TransitionSummaryReport, TransitionSummaryReportRow, \
    TransitionByStateClassSummaryReport, TransitionByStateClassSummaryReportRow

# TODO - simple or complicated? Could have simple and verbose serializers

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
        fields = ('id', 'name', 'pid', 'scenarios',)


class ScenarioSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='project-detail'
        )

    class Meta:
        model = Scenario
        fields = '__all__'


class StratumSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = Stratum
        fields = ('id', 'stratum_id', 'name', 'color', 'project',)


class StateClassSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = StateClass
        fields = ('id', 'stateclass_id', 'name', 'color', 'development', 'structure', 'project',)


class TransitionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionType
        fields = '__all__'


class TransitionGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransitionGroup
        fields = '__all__'


class TransitionTypeGroupSerializer(serializers.ModelSerializer):

    transition_type = TransitionTypeSerializer(read_only=True)
    transition_group = TransitionGroupSerializer(read_only=True)

    class Meta:
        model = TransitionTypeGroup
        fields = ('transition_type', 'transition_group', 'is_primary')


class ProjectDefinitionsSerializer(serializers.Serializer):
    """
        Special serializer for a one-stop-shop for collecting all
        project definitions in one location
    """

    stateclasses = StateClassSerializer(many=True, read_only=True)
    strata = StratumSerializer(many=True, read_only=True)
    transition_types = TransitionTypeSerializer(many=True, read_only=True)
    transition_groups = TransitionGroupSerializer(many=True, read_only=True)
    transition_type_groups = TransitionTypeGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('stateclasses', 'strata', 'transition_types', 'transition_groups',
            'transition_type_groups',)


class TransitionSerializer(serializers.ModelSerializer):
    
    stratum_src = StratumSerializer(many=False, read_only=True)
    stateclass_src = StateClassSerializer(many=False, read_only=True)

    class Meta:
        model = Transition
        fields = '__all__'


class StateClassSummaryReportRowSerializer(serializers.ModelSerializer):

    #stratum = StratumSerializer(many=False, read_only=True)
    #stateclass = StateClassSerializer(many=False, read_only=True)

    class Meta:
        model = StateClassSummaryReportRow
        fields = ('iteration','timestep','stratum','stateclass',
            'amount','proportion_of_landscape', 'proportion_of_stratum')

class StateClassSummaryReportSerializer(serializers.ModelSerializer):

    scenario = ScenarioSerializer(many=False, read_only=True)
    stateclass_results = StateClassSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = StateClassSummaryReport
        fields = ('id', 'scenario','stateclass_results',)

class TransitionSummaryReportRowSerializer(serializers.ModelSerializer):

    #stratum = StratumSerializer(many=False, read_only=True)
    #stateclass = StateClassSerializer(many=False, read_only=True)
    #transition_group = TransitionGroupSerializer(many=False, read_only=True)

    class Meta:
        model = TransitionSummaryReportRow
        fields = ('iteration','timestep','stratum', 'amount','transition_group',)

class TransitionSummaryReportSerializer(serializers.ModelSerializer):

    scenario = ScenarioSerializer(many=False, read_only=True)
    transition_results = TransitionSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = TransitionSummaryReport
        fields = ('id', 'scenario','transition_results',)

class TransitionByStateClassSummaryReportRowSerializer(serializers.ModelSerializer):

    #stratum = StratumSerializer(many=False, read_only=True)
    #stateclass_src = StateClassSerializer(many=False, read_only=True)
    #stateclass_dest = StateClassSerializer(many=False, read_only=True)
    #transition_type = TransitionTypeSerializer(many=False, read_only=True)

    class Meta:
        model = TransitionByStateClassSummaryReportRow
        fields = ('iteration','timestep','stratum','stateclass_src', 'stateclass_dest',
            'amount','transition_type',)

class TransitionByStateClassSummaryReportSerializer(serializers.ModelSerializer):

    scenario = ScenarioSerializer(many=False, read_only=True)
    transition_stateclass_results = TransitionByStateClassSummaryReportRowSerializer(many=True, read_only=True)
    
    class Meta:
        model = TransitionByStateClassSummaryReport
        fields = ('id', 'scenario','transition_stateclass_results',)