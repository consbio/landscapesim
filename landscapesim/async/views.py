from rest_framework.viewsets import GenericViewSet, mixins

from landscapesim.async.serializers import RunModelReadOnlySerializer, RunModelCreateSerializer
from landscapesim.models import RunScenarioModel


class RunModelViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RunScenarioModel.objects.all()
    lookup_field = 'uuid'
    serializer_class = RunModelReadOnlySerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = RunModelCreateSerializer
        return serializer_class
