from rest_framework import serializers
from django_stsim.models import Library, Project, Scenario


class LibrarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Library
        fields = ('name',)


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scenario
        fields = '__all__'
        #fields = ('name', 'is_result', 'sid')
