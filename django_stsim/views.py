from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ParseError

from django_stsim.models import Library, Project, Scenario, Stratum, StateClass, \
 TransitionType, TransitionGroup, TransitionTypeGroup, Transition, StateClassSummaryReport
from django_stsim.serializers import LibrarySerializer, ProjectSerializer, ScenarioSerializer, \
    StratumSerializer, StateClassSerializer, TransitionTypeSerializer, TransitionGroupSerializer, \
    TransitionTypeGroupSerializer, TransitionSerializer, StateClassSummaryReportSerializer

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
        context = {'request': self.request}
        stateclasses = StateClassSerializer(StateClass.objects.filter(project=project), many=True, context=context).data
        strata = StratumSerializer(Stratum.objects.filter(project=project), many=True, context=context).data
        transition_types = TransitionTypeSerializer(TransitionType.objects.filter(project=project), many=True, context=context).data
        transition_groups = TransitionGroupSerializer(TransitionGroup.objects.filter(project=project), many=True, context=context).data
        transition_type_groups = TransitionTypeGroupSerializer(TransitionTypeGroup.objects.filter(project=project), many=True, context=context).data
        return Response({
            'state_classes': stateclasses,
            'strata': strata,
            'transition_types': transition_types,
            'transition_groups': transition_groups,
            'transition_type_groups': transition_type_groups
        })

    @detail_route(methods=['get'])
    def scenarios(self, *args, **kwargs):
        return Response(ScenarioSerializer(Scenario.objects.filter(project=self.get_object()), many=True).data)


class ScenarioViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    @detail_route(methods=['get'])
    def project(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ProjectSerializer(self.get_object().project, context=context).data)

    @detail_route(methods=['get'])
    def library(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(LibrarySerializer(self.get_object().project.library, context=context).data)

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

    def get_queryset(self):
        pid = self.request.query_params.get('pid', None)
        if pid is None:
            return self.queryset
        return self.queryset.filter(project__pid=pid)


class StateClassViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateClass.objects.all()
    serializer_class = StateClassSerializer


class TransitionTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionType.objects.all()
    serializer_class = TransitionTypeSerializer

    @detail_route(methods=['get'])
    def groups(self, *args, **kwargs):
        return Response(TransitionTypeGroupSerializer(
            TransitionTypeGroup.objects.filter(transition_type=self.get_object()), many=True).data)


class TransitionGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionGroup.objects.all()
    serializer_class = TransitionGroupSerializer

    @detail_route(methods=['get'])
    def types(self, *args, **kwargs):
        return Response(TransitionTypeGroupSerializer(
            TransitionTypeGroup.objects.filter(transition_group=self.get_object()), many=True).data)


class TransitionTypeGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionTypeGroup.objects.all()
    serializer_class = TransitionTypeGroupSerializer


class TransitionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer


class StateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateClassSummaryReport.objects.all()
    serializer_class = StateClassSummaryReportSerializer