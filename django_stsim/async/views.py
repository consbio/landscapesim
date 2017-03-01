from rest_framework.viewsets import GenericViewSet, mixins

from django_stsim.models import AsyncJobModel
from django_stsim.async.serializers import RunModelSerializer, GenerateReportSerializer


class AsyncJobViewsetBase(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = AsyncJobModel.objects.all()
    lookup_field = 'uuid'


class RunModelViewset(AsyncJobViewsetBase):
    serializer_class = RunModelSerializer


class GenerateReportViewset(AsyncJobViewsetBase):
    serializer_class = GenerateReportSerializer
