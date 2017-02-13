from rest_framework import serializers
from django_stsim.models import Library, Project, Scenario, Stratum, StateClass


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
        fields = ('id', 'stateclass_id','color','development','structure', 'project',)


class StratumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stratum
        fields = ('id', 'stratum_id', 'name', 'color', 'project',)


class StateClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = StateClass
        fields = '__all__'