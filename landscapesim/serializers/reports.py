"""
    Model serializers for models that contain information for reports for a given scenario.
"""

from rest_framework import serializers
from landscapesim.models import Scenario, \
    StateClassSummaryReport, StateClassSummaryReportRow, \
    TransitionSummaryReport, TransitionSummaryReportRow, \
    TransitionByStateClassSummaryReport, TransitionByStateClassSummaryReportRow, \
    StateAttributeSummaryReport, StateAttributeSummaryReportRow, \
    TransitionAttributeSummaryReport, TransitionAttributeSummaryReportRow


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
        model = Scenario
        fields = ('stateclass_summary_report', 'transition_summary_report', 'transition_by_sc_summary_report',
                  'state_attribute_summary_report', 'transition_attribute_summary_report',)
