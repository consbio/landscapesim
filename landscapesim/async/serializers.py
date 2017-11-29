"""
    Serializers for consuming job submissions for running models and generating reports
"""
import json
import os
from uuid import uuid4

from django.conf import settings
from rest_framework import serializers

from landscapesim.async.tasks import run_model
from landscapesim.common.geojson import rasterize_geojson
from landscapesim.models import Library, Project, Scenario, RunScenarioModel, TransitionGroup
from landscapesim.serializers import imports

STSIM_MULTIPLIER_DIR = getattr(settings, 'STSIM_MULTIPLIER_DIR')

# Need to know the library_name, and the inner project and scenario ids for any job
BASIC_JOB_INPUTS = ['library_name', 'pid', 'sid']


class AsyncJobSerializerMixin(object):
    """
        A base mixin for serializing the inputs and outputs, and validating that the minimum job info is provided.
    """

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
    """ Initial model run validation """

    model_status = serializers.CharField(read_only=True)

    class Meta:
        model = RunScenarioModel
        fields = ('uuid', 'created', 'status', 'model_status', 'progress', 'inputs', 'outputs', 'parent_scenario', 'result_scenario')
        read_only_fields = ('uuid', 'created', 'status', 'outputs', 'parent_scenario', 'result_scenario')

    def validate_inputs(self, value):
        value = super(RunModelSerializer, self).validate_inputs(value)
        if value:
            try:
                config = value['config']

                # Ensure that all configuration keys are supplied. Validation of this imports is handled asynchronously
                # within the Celery.run_model task.
                if not all(x[0] in config.keys() for x in imports.CONFIG_INPUTS + imports.VALUE_INPUTS):
                    raise serializers.ValidationError(
                        'Missing configurations within {}. Got the following configuration keys: {}'.format(
                            imports.CONFIG_INPUTS, list(config.keys())
                        )
                    )

                # Return the value unchanged
                return value

            except ValueError:
                raise serializers.ValidationError('Malformed configuration')
        return {}

    def create(self, validated_data):
        library_name = validated_data['inputs']['library_name']
        pid = validated_data['inputs']['pid']
        sid = validated_data['inputs']['sid']
        lib = Library.objects.get(name__exact=library_name)
        proj = Project.objects.get(library=lib, pid=int(pid))
        parent_scenario = Scenario.objects.get(project=proj, sid=int(sid))
        result = run_model.delay(library_name, sid)
        return RunScenarioModel.objects.create(
            parent_scenario=parent_scenario,
            celery_id=result.id,
            inputs=json.dumps(validated_data['inputs']),
            model_status='waiting'
        )
