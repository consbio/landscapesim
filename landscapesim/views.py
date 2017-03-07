from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route  # TODO - use list_route for scenario dependencies?
from rest_framework.exceptions import ParseError

# Project models
from landscapesim.models import Library, Project, Scenario, Terminology, DistributionType, Stratum, SecondaryStratum, StateClass, \
    TransitionType, TransitionGroup, TransitionTypeGroup, TransitionMultiplierType, AttributeGroup, StateAttributeType,\
    TransitionAttributeType

# Scenario models
from landscapesim.models import DistributionValue, OutputOption, RunControl, DeterministicTransition, Transition, \
    InitialConditionsNonSpatial, InitialConditionsNonSpatialDistribution, TransitionTarget, TransitionMultiplierValue, \
    TransitionSizeDistribution, TransitionSizePrioritization, TransitionSpatialMultiplier, StateAttributeValue, \
    TransitionAttributeValue, TransitionAttributeTarget

# Reports
from landscapesim.models import \
    StateClassSummaryReport, TransitionSummaryReport, TransitionByStateClassSummaryReport, \
    StateAttributeSummaryReport, TransitionAttributeSummaryReport

# Serialization glue # TODO - split
from landscapesim.serializers import LibrarySerializer, ProjectSerializer, ScenarioSerializer, \
    StratumSerializer, SecondaryStratumSerializer, StateClassSerializer, TransitionTypeSerializer, \
    TransitionGroupSerializer, TransitionTypeGroupSerializer, DeterministicTransitionSerializer, TransitionSerializer, \
    InitialConditionsNonSpatialSerializer, InitialConditionsNonSpatialDistributionSerializer, \
    StateClassSummaryReportSerializer, TransitionSummaryReportSerializer, TransitionByStateClassSummaryReportSerializer, \
    RunControlSerializer, OutputOptionSerializer, TransitionMultiplierTypeSerializer, AttributeGroupSerializer, \
    StateAttributeTypeSerializer, TransitionAttributeTypeSerializer, TransitionTargetSerializer, \
    TransitionSizeDistributionSerializer, TransitionSizePrioritizationSerializer, TransitionSpatialMultiplierSerializer, \
    StateAttributeValueSerializer, TransitionAttributeValueSerializer, TransitionAttributeTargetSerializer, \
    TransitionMultiplierValueSerializer

# Special-purpose serializers
from landscapesim.serializers import ProjectDefinitionsSerializer, QueryScenarioReportSerializer, ScenarioValuesSerializer

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
        return Response(ProjectDefinitionsSerializer(self.get_object(), context=context).data)

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

    @detail_route(methods=['get'])
    def outputoptions(self, *args, **kwargs):
        context= {'request': self.request}
        return Response(OutputOptionSerializer(OutputOption.objects.filter(
            scenario=self.get_object()).first(), context=context).data)

    @detail_route(methods=['get'])
    def reports(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(QueryScenarioReportSerializer(self.get_object(), context=context).data)

    @detail_route(methods=['get'])
    def values(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ScenarioValuesSerializer(self.get_object(), context=context).data)

    # TODO - Add terminology as detail route


    # TODO - include these as a single detail route?
    # TODOr - Add transitions
    # TODOr - Add initial conditions
    # TODOr - Add transition targets
    # TODOr - Add state attribute values
    # TODOr - Add transition attribute targets
    # TODOr - Add transition attribute values (blend w/ targets?)
    # TODOr - Add transition multipliers

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


class SecondaryStratumViewset(viewsets.ReadOnlyModelViewSet):
    queryset = SecondaryStratum.objects.all()
    serializer_class = SecondaryStratumSerializer


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


class TransitionMultiplierTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionMultiplierType.objects.all()
    serializer_class = TransitionMultiplierTypeSerializer


class AttributeGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = AttributeGroup.objects.all()
    serializer_class = AttributeGroupSerializer


class StateAttributeTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateAttributeType.objects.all()
    serializer_class = StateAttributeTypeSerializer


class TransitionAttributeTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionAttributeType.objects.all()
    serializer_class = TransitionAttributeTypeSerializer


""" Scenario configuration viewsets """


class DeterministicTransitionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = DeterministicTransition.objects.all()
    serializer_class = DeterministicTransitionSerializer


class TransitionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer


class InitialConditionsNonSpatialViewset(viewsets.ReadOnlyModelViewSet):
    queryset = InitialConditionsNonSpatial.objects.all()
    serializer_class = InitialConditionsNonSpatialSerializer


class InitialConditionsNonSpatialDistributionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = InitialConditionsNonSpatialDistribution.objects.all()
    serializer_class = InitialConditionsNonSpatialDistributionSerializer


class TransitionTargetViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionTarget.objects.all()
    serializer_class = TransitionTargetSerializer


class TransitionMultiplierValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionMultiplierValue.objects.all()
    serializer_class = TransitionMultiplierValueSerializer


class TransitionSizeDistributionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionSizeDistribution.objects.all()
    serializer_class = TransitionSizeDistributionSerializer


class TransitionSizePrioritizationViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionSizePrioritization.objects.all()
    serializer_class = TransitionSizePrioritizationSerializer


class StateAttributeValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateAttributeValue.objects.all()
    serializer_class = StateAttributeValueSerializer


class TransitionAttributeValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionAttributeValue.objects.all()
    serializer_class = TransitionAttributeValueSerializer


class TransitionAttributeTargetViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionAttributeTarget.objects.all()
    serializer_class = TransitionAttributeTargetSerializer


""" Report viewsets """


class StateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateClassSummaryReport.objects.all()
    serializer_class = StateClassSummaryReportSerializer


class TransitionSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionSummaryReport.objects.all()
    serializer_class = TransitionSummaryReportSerializer


class TransitionByStateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionByStateClassSummaryReport.objects.all()
    serializer_class = TransitionByStateClassSummaryReportSerializer


class StateAttributeSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = StateAttributeSummaryReport.objects.all()
    serializer_class = TransitionByStateClassSummaryReportSerializer


class TransitionAttributeSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionAttributeSummaryReport.objects.all()
    serializer_class = TransitionByStateClassSummaryReportSerializer


