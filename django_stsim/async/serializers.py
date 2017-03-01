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

from rest_framework import serializers
from django_stsim.models import AsyncJobModel
import json
from django_stsim.async.tasks import run_model, generate_report

REGISTERED_JOBS = ['run-model', 'generate-report']

BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']

REGISTERED_REPORTS = [
    'stateclass-summary', 'transition-summary', 'transition-stateclass-summary',
    'state-attributes', 'transition-attributes'
]


class AsyncJobSerializerBase(serializers.ModelSerializer):

    # TODO - have the below available in subclasses, and have two separate serializers

    status = serializers.CharField(read_only=True)
    inputs = serializers.JSONField(allow_null=True)
    outputs = serializers.JSONField(read_only=True)

    job_inputs = []

    class Meta:
        model = AsyncJobModel
        fields = ('uuid', 'job', 'created', 'status', 'inputs', 'outputs')
        read_only_fields = ('uuid', 'created', 'status')

    def validate_inputs(self, value):
        if value:
            try:
                print(value)
                if all(x in value.keys() for x in self.job_inputs):
                    return value
                else:
                    raise serializers.ValidationError('Missing one of {}'.format(self.job_inputs))
            except ValueError:
                raise serializers.ValidationError('Invalid input JSON')

        return {}

    def validate_job(self, value):
        if value not in REGISTERED_JOBS:
            raise serializers.ValidationError('Invalid job name')
        return value


class RunModelSerializer(AsyncJobSerializerBase):

    job_inputs = BASIC_JOB_INPUTS

    def validate(self, attrs):

        if attrs['job'] != 'run-model':
            raise serializers.ValidationError('Supplied job does not match "run-model"')

        # TODO - validate other inputs (transition probabilities, state/transition attributes, etc...)

        return attrs

    def create(self, validated_data):

        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        result = run_model.delay(library_name, pid, sid)
        return AsyncJobModel.objects.create(
            job=validated_data['job'], celery_id=result.id, inputs=json.dumps(validated_data['inputs'])
        )


class GenerateReportSerializer(AsyncJobSerializerBase):

    job_inputs = BASIC_JOB_INPUTS + ['report_name']

    def validate(self, attrs):

        if attrs['job'] != 'generate-report':
            raise serializers.ValidationError('Supplied job does not match "generate-report"')

        return attrs

    def create(self, validated_data):

        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        report_name = validated_data['inputs']['report_name']
        result = generate_report.delay(library_name, pid, sid, report_name)
        return AsyncJobModel.objects.create(
            job=validated_data['job'], celery_id=result.id, inputs=json.dumps(validated_data['inputs'])
        )
