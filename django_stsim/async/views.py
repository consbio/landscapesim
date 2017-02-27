from rest_framework.viewsets import GenericViewSet, mixins

from django_stsim.models import AsyncJobModel
from django_stsim.async.serializers import AsyncJobSerializer


class AsyncJobViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = AsyncJobModel.objects.all()
    serializer_class = AsyncJobSerializer
    lookup_field = 'uuid'


# only need the below

class RunModelViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):

    raise NotImplementedError()


class GenerateReportViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):

    raise NotImplementedError()

