from rest_framework.viewsets import GenericViewSet, mixins

from landscapesim.models import RunScenarioModel
from landscapesim.async.serializers import RunModelSerializer


class RunModelViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RunScenarioModel.objects.all()
    lookup_field = 'uuid'
    serializer_class = RunModelSerializer
