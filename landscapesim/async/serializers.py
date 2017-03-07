"""
    Serializers for consuming job submissions for running models and generating reports
"""

import json
from rest_framework import serializers
from landscapesim.models import Library, Project, Scenario, \
    RunScenarioModel, GenerateReportModel
from landscapesim.serializers import ScenarioSerializer
from landscapesim.async.tasks import run_model, generate_report
from django.core import exceptions

REGISTERED_JOBS = ['run-model', 'generate-report']

BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']

REGISTERED_REPORTS = [
    'stateclass-summary', 'transition-summary', 'transition-stateclass-summary',
    'state-attributes', 'transition-attributes'
]


class AsyncJobSerializerMixin(object):

    status = serializers.CharField(read_only=True)
    inputs = serializers.JSONField(allow_null=True)
    outputs = serializers.JSONField(read_only=True)

    job_inputs = BASIC_JOB_INPUTS

    def validate_inputs(self, value):
        if value:
            try:
                value = json.loads(value)
                if all(x in value.keys() for x in self.job_inputs):
                    return value
                else:
                    raise serializers.ValidationError('Missing one of {}'.format(self.job_inputs))
            except ValueError:
                raise serializers.ValidationError('Invalid input JSON')

        return {}


class RunModelSerializer(AsyncJobSerializerMixin, serializers.ModelSerializer):

    parent_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')
    result_scenario = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='scenario-detail')

    class Meta:
        model = RunScenarioModel
        fields = ('uuid', 'created', 'status', 'inputs', 'outputs', 'parent_scenario', 'result_scenario')
        read_only_fields = ('uuid', 'created', 'status', 'outputs', 'parent_scenario', 'result_scenario')

    def validate(self, attrs):

        # TODO - validate other inputs (transition probabilities, state/transition attributes, etc...)
        # This will be necessary to import other items if we want to run the new values
        # We don't need to add database rows into the system as those will be captured after a model run is complete
        # For now, it is enough that we can run scenarios as stock models

        return attrs

    def create(self, validated_data):

        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        lib = Library.objects.get(name__exact=library_name)
        proj = Project.objects.get(library=lib, pid=int(pid))
        parent_scenario = Scenario.objects.get(project=proj, sid=int(sid))
        result = run_model.delay(library_name, pid, sid)
        return RunScenarioModel.objects.create(
            parent_scenario=parent_scenario,
            celery_id=result.id,
            inputs=json.dumps(validated_data['inputs'])
        )


class GenerateReportSerializer(AsyncJobSerializerMixin, serializers.ModelSerializer):

    report_name = serializers.CharField()

    class Meta:
        model = GenerateReportModel
        fields = ('uuid', 'created', 'status', 'report_name', 'inputs', 'outputs')
        read_only_fields = ('uuid', 'created', 'status', 'outputs')

    def validate(self, attrs):

        if attrs['report_name'] not in REGISTERED_REPORTS:
            raise serializers.ValidationError('No report with name {} available'.format(attrs['report_name']))

        # Throw exceptions if scenario select is not a result scenario or does not exist
        inputs = attrs['inputs']
        try:
            scenario = Scenario.objects.get(
                sid=int(inputs['sid']),
                project__pid=int(inputs['pid']),
                project__library__name__exact=inputs['library_name'])
            if not scenario.is_result:
                raise serializers.ValidationError('Cannot run a report on non-result scenarios.')
        except exceptions.ObjectDoesNotExist:
            raise serializers.ValidationError('Cannot find scenario with provided arguments.')

        return attrs

    def create(self, validated_data):

        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        report_name = validated_data['report_name']
        result = generate_report.delay(library_name, pid, sid, report_name)
        return GenerateReportModel.objects.create(
            report_name=report_name,
            celery_id=result.id,
            inputs=json.dumps(validated_data['inputs'])
        )
