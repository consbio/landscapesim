from rest_framework.viewsets import GenericViewSet, mixins

from landscapesim.async.serializers import RunModelSerializer
from landscapesim.models import RunScenarioModel


class RunModelViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RunScenarioModel.objects.all()
    lookup_field = 'uuid'
    serializer_class = RunModelSerializer
