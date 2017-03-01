from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ParseError

from django_stsim.models import Library, Project, Scenario, Stratum, StateClass, \
    TransitionType, TransitionGroup, TransitionTypeGroup, Transition, StateClassSummaryReport, \
    TransitionSummaryReport, TransitionByStateClassSummaryReport, RunControl, OutputOption
from django_stsim.serializers import LibrarySerializer, ProjectSerializer, ScenarioSerializer, \
    StratumSerializer, StateClassSerializer, TransitionTypeSerializer, TransitionGroupSerializer, \
    TransitionTypeGroupSerializer, TransitionSerializer, StateClassSummaryReportSerializer, \
    TransitionSummaryReportSerializer, TransitionByStateClassSummaryReportSerializer, \
    RunControlSerializer, OutputOptionSerializer
from django_stsim.serializers import ProjectDefinitionsSerializer

# TODO - Discuss integration of spatial layers into models


class LibraryViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer


class ProjectViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @detail_route(methods=['get'])
    def definitions(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ProjectDefinitionsSerializer(
            self.queryset.filter(pk=self.get_object().pk), many=True, context=context).data)

    @detail_route(methods=['get'])
    def scenarios(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ScenarioSerializer(Scenario.objects.filter(project=self.get_object()), many=True, context=context).data)


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

    @detail_route(methods=['get'])
    def runcontrol(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(RunControlSerializer(RunControl.objects.filter(
            scenario=self.get_object()).first(), context=context).data
        )

    # TODO - Add transitions
    # TODO - Add initial conditions
    # TODO - Add transition targets
    # TODO - Add state attribute values
    # TODO - Add transition attribute targets
    # TODO - Add transition attribute values (blend w/ targets?)
    # TODO - Add transition multipliers

    def get_queryset(self):
        if not self.request.query_params.get('results_only'):
            return self.queryset
        else:
            is_result = self.request.query_params.get('results_only')
            if is_result not in ['true','false']:
                raise ParseError('Was not true or false.')
            return self.queryset.filter(is_result=is_result=='true')


class RunControlViewset(viewsets.ReadOnlyModelViewSet):
    queryset = RunControl.objects.all()
    serializer_class = RunControlSerializer


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
    def groups(self, *args, **kwargs):      # TODO - should this be just the TransitionGroups, and not TransitionTypeGroups?
        return Response(TransitionTypeGroupSerializer(
            TransitionTypeGroup.objects.filter(transition_type=self.get_object()), many=True).data)


class TransitionGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionGroup.objects.all()
    serializer_class = TransitionGroupSerializer

    @detail_route(methods=['get'])
    def types(self, *args, **kwargs):       # TODO - should this be just the TransitionTypes, and not TransitionTypeGroups?
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


class TransitionSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionSummaryReport.objects.all()
    serializer_class = TransitionSummaryReportSerializer


class TransitionByStateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionByStateClassSummaryReport.objects.all()
    serializer_class = TransitionByStateClassSummaryReportSerializer


class OutputOptionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = OutputOption.objects.all()
    serializer_class = OutputOptionSerializer
