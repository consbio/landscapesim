from rest_framework import serializers
from django_stsim.models import Library, Project, Scenario, Stratum, StateClass,\
    TransitionType, TransitionGroup, TransitionTypeGroup, Transition, \
    StateClassSummaryReport, StateClassSummaryReportRow


class LibrarySerializer(serializers.ModelSerializer):

    projects = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='project-detail',
        )

    class Meta:
        model = Library
        fields = ('name', 'projects', 'id',)


class ProjectSerializer(serializers.ModelSerializer):

    scenarios = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='scenario-detail',
        )

    class Meta:
        model = Project
        fields = ('name', 'pid', 'scenarios', 'id',)


class ScenarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scenario
        fields = '__all__'


class StratumSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = Stratum
        fields = ('id', 'stratum_id', 'name', 'color', 'project',)


class StateClassSerializer(serializers.ModelSerializer):

    project = serializers.HyperlinkedRelatedField(many=False, view_name='project-detail', read_only=True)

    class Meta:
        model = StateClass
        fields = ('id', 'stateclass_id', 'color', 'development', 'structure', 'project',)


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
        fields = ('transition_type', 'transition_group', 'is_primary')


class TransitionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Transition
        fields = '__all__'


class StateClassSummaryReportRowSerializer(serializers.ModelSerializer):

    stratum = StratumSerializer(many=False, read_only=True)
    stateclass = StateClassSerializer(many=False, read_only=True)

    class Meta:
        model = StateClassSummaryReportRow
        fields = ('iteration','timestep','stratum','stateclass',
            'amount','proportion_of_landscape', 'proportion_of_stratum')

class StateClassSummaryReportSerializer(serializers.ModelSerializer):

    scenario = ScenarioSerializer(many=False, read_only=True)
    stateclass_results = StateClassSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = StateClassSummaryReport
        fields = ('scenario','stateclass_results',)