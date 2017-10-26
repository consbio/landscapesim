"""
    Model serializers for models that contain information for reports for a given scenario.
"""

from rest_framework import serializers

from landscapesim import models


class GenerateReportSerializer(serializers.Serializer):
    configuration = serializers.JSONField()


class StateClassSummaryReportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StateClassSummaryReportRow
        fields = '__all__'


class StateClassSummaryReportSerializer(serializers.ModelSerializer):
    results = StateClassSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = models.StateClassSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionSummaryReportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionSummaryReportRow
        fields = '__all__'


class TransitionSummaryReportSerializer(serializers.ModelSerializer):
    results = TransitionSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = models.TransitionSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionByStateClassSummaryReportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionByStateClassSummaryReportRow
        fields = '__all__'


class TransitionByStateClassSummaryReportSerializer(serializers.ModelSerializer):
    results = TransitionByStateClassSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = models.TransitionByStateClassSummaryReport
        fields = ('id', 'scenario', 'results',)


class StateAttributeSummaryReportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StateAttributeSummaryReportRow
        fields = '__all__'


class StateAttributeSummaryReportSerializer(serializers.ModelSerializer):
    results = StateAttributeSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = models.StateAttributeSummaryReport
        fields = ('id', 'scenario', 'results',)


class TransitionAttributeSummaryReportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransitionAttributeSummaryReportRow
        fields = '__all__'


class TransitionAttributeSummaryReportSerializer(serializers.ModelSerializer):
    results = TransitionAttributeSummaryReportRowSerializer(many=True, read_only=True)

    class Meta:
        model = models.TransitionAttributeSummaryReport
        fields = ('id', 'scenario', 'results',)


class QueryScenarioReportSerializer(serializers.ModelSerializer):
    """
        Convenient serializer for connecting to available reports for a given scenario
    """

    stateclass_summary_report = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='stateclasssummaryreport-detail'
    )

    transition_summary_report = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='transitionsummaryreport-detail'
    )

    transition_by_sc_summary_report = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='transitionbystateclasssummaryreport-detail'
    )

    state_attribute_summary_report = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='stateattributesummaryreport-detail'
    )

    transition_attribute_summary_report = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='transitionattributesummaryreport-detail'
    )

    class Meta:
        model = models.Scenario
        fields = ('stateclass_summary_report', 'transition_summary_report', 'transition_by_sc_summary_report',
                  'state_attribute_summary_report', 'transition_attribute_summary_report',)
