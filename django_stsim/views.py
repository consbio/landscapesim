from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from django_stsim.models import Library, Project, Scenario, Stratum, StateClass
from django_stsim.serializers import LibrarySerializer, ProjectSerializer, ScenarioSerializer
from django_stsim.serializers import StratumSerializer, StateClassSerializer

from stsimpy import STSimConsole


class LibraryViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer


class ProjectViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @detail_route(methods=['get'])
    def definitions(self, *args, **kwargs):
        project = self.get_object()
        lib = project.library
        stateclasses = StateClassSerializer(StateClass.objects.filter(project=project), many=True).data
        strata = StratumSerializer(Stratum.objects.filter(project=project), many=True).data
        return Response({'state_classes':stateclasses,'strata':strata})


class ScenarioViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    filter_fields = ('results_only',)

    @detail_route(methods=['get'])
    def project(self, *args, **kwargs):
        return Response({'pid':self.get_object().project.pid})

    @detail_route(methods=['get'])
    def library(self, *args, **kwargs):
        return Response({'library':self.get_object().project.library.name})

    def get_queryset(self):
        if not self.request.query_params.get('results_only'):
            return self.queryset
        else:
            is_result = self.request.query_params.get('results_only')
            if is_result not in ['true','false']:
                raise ParseError('Was not true or false.')
            return self.queryset.filter(is_result=is_result=='true')


class StratumViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Stratum.objects.all()
    serializer_class = StratumSerializer


class StateClassViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateClass.objects.all()
    serializer_class = StateClassSerializer

