from rest_framework.viewsets import GenericViewSet, mixins

from django_stsim.models import RunScenarioModel, GenerateReportModel
from django_stsim.async.serializers import RunModelSerializer, GenerateReportSerializer


class RunModelViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RunScenarioModel.objects.all()
    lookup_field = 'uuid'
    serializer_class = RunModelSerializer


class GenerateReportViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = GenerateReportModel.objects.all()
    lookup_field = 'uuid'
    serializer_class = GenerateReportSerializer
