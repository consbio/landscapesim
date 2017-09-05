"""
    Model serializers for models that operate on a project basis, within a given library.
"""

from rest_framework import serializers

from landscapesim import models


class LibrarySerializer(serializers.ModelSerializer):
    projects = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='project-detail',
        )

    class Meta:
        model = models.Library
        fields = ('id', 'name', 'projects',)


class ProjectSerializer(serializers.ModelSerializer):
    scenarios = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='scenario-detail',
        )

    class Meta:
        model = models.Project
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):
    project = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='project-detail'
        )

    class Meta:
        model = models.Scenario
        fields = '__all__'


class TerminologySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Terminology
        fields = '__all__'


class DistributionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DistributionType
        fields = '__all__'


class StratumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stratum
        fields = '__all__'


class SecondaryStratumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SecondaryStratum
        fields = '__all__'


class StateClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StateClass
        fields = '__all__'


class TransitionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionType
        fields = '__all__'


class TransitionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionGroup
        fields = '__all__'


class TransitionTypeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionTypeGroup
        fields = '__all__'


class TransitionMultiplierTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionMultiplierType
        fields = '__all__'


class AttributeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttributeGroup
        fields = '__all__'


class StateAttributeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StateAttributeType
        fields = '__all__'


class TransitionAttributeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionAttributeType
        fields = '__all__'


class ProjectDefinitionsSerializer(serializers.Serializer):
    """
        Special serializer for a one-stop-shop for collecting all
        project definitions in one location
    """

    terminology = TerminologySerializer(read_only=True, many=False)
    stateclasses = StateClassSerializer(read_only=True, many=True)
    strata = StratumSerializer(many=True, read_only=True)
    transition_types = TransitionTypeSerializer(many=True, read_only=True)
    transition_groups = TransitionGroupSerializer(many=True, read_only=True)
    transition_type_groups = TransitionTypeGroupSerializer(many=True, read_only=True)
    transition_attributes = TransitionAttributeTypeSerializer(many=True, read_only=True)
    state_attributes = StateAttributeTypeSerializer(many=True, read_only=True)
    attribute_groups = AttributeGroupSerializer(many=True, read_only=True)

    class Meta:
        fields = ('terminology', 'stateclasses', 'strata', 'transition_types', 'transition_groups',
                  'transition_type_groups', 'transition_attributes', 'state_attributes',
                  'attribute_groups',)
