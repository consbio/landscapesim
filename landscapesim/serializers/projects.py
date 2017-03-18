"""
    Model serializers for models that operate on a project basis, within a given library.
"""

from rest_framework import serializers
from landscapesim.models import Library, Project, Scenario, Terminology, DistributionType, \
    Stratum, SecondaryStratum, StateClass, TransitionType, TransitionGroup, TransitionTypeGroup, \
    TransitionMultiplierType, AttributeGroup, StateAttributeType, TransitionAttributeType


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
    class Meta:
        model = Stratum
        fields = '__all__'


class SecondaryStratumSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryStratum
        fields = '__all__'


class StateClassSerializer(serializers.ModelSerializer):
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

    terminology = TerminologySerializer(read_only=True, many=False)
    stateclasses = StateClassSerializer(read_only=True, many=True)
    strata = StratumSerializer(many=True, read_only=True)
    transition_types = TransitionTypeSerializer(many=True, read_only=True)
    transition_groups = TransitionGroupSerializer(many=True, read_only=True)
    transition_type_groups = TransitionTypeGroupSerializer(many=True, read_only=True)
    transition_attribute_types = TransitionAttributeTypeSerializer(many=True, read_only=True)
    state_attribute_types = StateAttributeTypeSerializer(many=True, read_only=True)
    attribute_groups = AttributeGroupSerializer(many=True, read_only=True)

    class Meta:
        fields = ('terminology', 'stateclasses', 'strata', 'transition_types', 'transition_groups',
                  'transition_type_groups', 'transition_attribute_types', 'state_attribute_types',
                  'attribute_groups',)

