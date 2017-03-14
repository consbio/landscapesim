from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from landscapesim.models import Library, Project, Scenario, DistributionType, Stratum, SecondaryStratum, StateClass, \
    TransitionType, TransitionGroup, TransitionTypeGroup, TransitionMultiplierType, AttributeGroup, StateAttributeType,\
    TransitionAttributeType
from landscapesim.serializers.projects import LibrarySerializer, ProjectSerializer, \
    ProjectDefinitionsSerializer, ScenarioSerializer, StratumSerializer, SecondaryStratumSerializer, \
    StateClassSerializer, TransitionTypeSerializer, TransitionGroupSerializer, TransitionTypeGroupSerializer, \
    TransitionMultiplierTypeSerializer, AttributeGroupSerializer, StateAttributeTypeSerializer, \
    TransitionAttributeTypeSerializer
from landscapesim.models import DistributionValue, DeterministicTransition, Transition, \
    InitialConditionsNonSpatial, InitialConditionsNonSpatialDistribution, InitialConditionsSpatial, TransitionTarget, \
    TransitionMultiplierValue, TransitionSizeDistribution, TransitionSizePrioritization, TransitionSpatialMultiplier, \
    StateAttributeValue, TransitionAttributeValue, TransitionAttributeTarget
from landscapesim.serializers.scenarios import ScenarioConfigSerializer, ScenarioValuesSerializer, \
    DeterministicTransitionSerializer, TransitionSerializer, InitialConditionsNonSpatialSerializer, \
    InitialConditionsNonSpatialDistributionSerializer, InitialConditionsSpatialSerializer, \
    TransitionTargetSerializer, TransitionMultiplierValueSerializer, TransitionSizeDistributionSerializer, \
    TransitionSizePrioritizationSerializer, TransitionSpatialMultiplierSerializer, \
    StateAttributeValueSerializer, TransitionAttributeValueSerializer, TransitionAttributeTargetSerializer
from landscapesim.models import StateClassSummaryReport, TransitionSummaryReport, TransitionByStateClassSummaryReport, \
    StateAttributeSummaryReport, TransitionAttributeSummaryReport
from landscapesim.serializers.reports import QueryScenarioReportSerializer, StateClassSummaryReportSerializer, \
    TransitionSummaryReportSerializer, TransitionByStateClassSummaryReportSerializer, \
    StateAttributeSummaryReportSerializer, TransitionAttributeSummaryReportSerializer


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
    def reports(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(QueryScenarioReportSerializer(self.get_object(), context=context).data)

    @detail_route(methods=['get'])
    def values(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ScenarioValuesSerializer(self.get_object(), context=context).data)

    @detail_route(methods=['get'])
    def config(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(ScenarioConfigSerializer(self.get_object(), context=context).data)

    def get_queryset(self):
        if not self.request.query_params.get('results_only'):
            return self.queryset
        else:
            is_result = self.request.query_params.get('results_only')
            if is_result not in ['true', 'false']:
                raise ParseError('Was not true or false.')
            return self.queryset.filter(is_result=is_result == 'true')


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
    def groups(self, *args, **kwargs):
        tgrps = [TransitionGroup.objects.get(pk=_['transition_group']) for _ in TransitionTypeGroup.objects.filter(
            transition_type=self.get_object()).values('transition_group')]
        return Response(TransitionGroupSerializer(tgrps, many=True).data)


class TransitionGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionGroup.objects.all()
    serializer_class = TransitionGroupSerializer

    @detail_route(methods=['get'])
    def types(self, *args, **kwargs):
        tts = [TransitionType.objects.get(pk=_['transition_type']) for _ in TransitionTypeGroup.objects.filter(
            transition_group=self.get_object()).values('transition_type')]
        return Response(TransitionTypeSerializer(tts, many=True).data)


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


class InitialConditionsSpatialViewset(viewsets.ReadOnlyModelViewSet):
    queryset = InitialConditionsSpatial.objects.all()
    serializer_class = InitialConditionsSpatialSerializer


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


class TransitionSpatialMultiplierViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionSpatialMultiplier.objects.all()
    serializer_class = TransitionSpatialMultiplierSerializer


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
    serializer_class = StateAttributeSummaryReportSerializer


class TransitionAttributeSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TransitionAttributeSummaryReport.objects.all()
    serializer_class = TransitionAttributeSummaryReportSerializer


