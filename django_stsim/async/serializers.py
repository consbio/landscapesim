"""
    TODO - We'll need to have an extensive if-else logic for handling the inputs to the model run
           from the frontend. Perhaps we should have a RunModelSerializer, and a GenerateReportSerializer
           That would make sense, as they're handled separately already.
           On the contrary, a job is a job, the run_model job is a single variant

    so, lets define the necessary inputs for model runs, including output options, and then
    allow the API to make requests to generate the necessary reports, if available from the
    output options made beforehand.

    I.e. one request for /jobs/run-model (POST - lib, sid, pid, <init_conditions>, <transitions>)
         one request for /jobs/generate-report (POST - lib, sid, pid, <[report1, report2, ...]>
         difference is that these reports would be dependent on the output options selected. Could be a UI decision?
"""
import json
from rest_framework import serializers
from django_stsim.models import Library, Project, Scenario, \
    RunScenarioModel, GenerateReportModel
from django_stsim.serializers import ScenarioSerializer
from django_stsim.async.tasks import run_model, generate_report

REGISTERED_JOBS = ['run-model', 'generate-report']

BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']

REGISTERED_REPORTS = [
    'stateclass-summary', 'transition-summary', 'transition-stateclass-summary',
    'state-attributes', 'transition-attributes'
]


class AsyncJobSerializerMixin(object):

    # TODO - have the below available in subclasses, and have two separate serializers

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

    parent_scenario = ScenarioSerializer(many=False, read_only=True)
    result_scenario = ScenarioSerializer(many=False, read_only=True)

    class Meta:
        model = RunScenarioModel
        fields = ('uuid', 'created', 'status', 'inputs', 'outputs', 'parent_scenario', 'result_scenario')
        read_only_fields = ('uuid', 'created', 'status', 'outputs', 'parent_scenario', 'result_scenario')

    def validate(self, attrs):

        # TODO - validate other inputs (transition probabilities, state/transition attributes, etc...)

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
