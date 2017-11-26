from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from landscapesim import models
from landscapesim.report import Report
from landscapesim.serializers import projects, reports, scenarios, regions


class LibraryViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Library.objects.all()
    serializer_class = projects.LibrarySerializer


class ProjectViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = projects.ProjectSerializer

    @detail_route(methods=['get'])
    def definitions(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(projects.ProjectDefinitionsSerializer(self.get_object(), context=context).data)

    @detail_route(methods=['get'])
    def scenarios(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(projects.ScenarioSerializer(
            models.Scenario.objects.filter(project=self.get_object()), many=True, context=context
        ).data)


class ScenarioViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Scenario.objects.all()
    serializer_class = projects.ScenarioSerializer

    @detail_route(methods=['get'])
    def project(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(projects.ProjectSerializer(self.get_object().project, context=context).data)

    @detail_route(methods=['get'])
    def library(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(projects.LibrarySerializer(self.get_object().project.library, context=context).data)

    @detail_route(methods=['get'])
    def reports(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(reports.QueryScenarioReportSerializer(self.get_object(), context=context).data)

    @detail_route(methods=['get'])
    def config(self, *args, **kwargs):
        context = {'request': self.request}
        return Response(scenarios.ScenarioConfigSerializer(self.get_object(), context=context).data)

    def get_queryset(self):
        if not self.request.query_params.get('results_only'):
            return self.queryset
        else:
            is_result = self.request.query_params.get('results_only')
            if is_result not in ['true', 'false']:
                raise ParseError('Was not true or false.')
            return self.queryset.filter(is_result=is_result == 'true')


class StratumViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Stratum.objects.all()
    serializer_class = projects.StratumSerializer

    def get_queryset(self):
        pid = self.request.query_params.get('pid', None)
        if pid is None:
            return self.queryset
        return self.queryset.filter(project__pid=pid)


class StateClassViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.StateClass.objects.all()
    serializer_class = projects.StateClassSerializer


class SecondaryStratumViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.SecondaryStratum.objects.all()
    serializer_class = projects.SecondaryStratumSerializer


class TransitionTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionType.objects.all()
    serializer_class = projects.TransitionTypeSerializer

    @detail_route(methods=['get'])
    def groups(self, *args, **kwargs):
        tgrps = [
            models.TransitionGroup.objects.get(pk=obj['transition_group'])
            for obj in models.TransitionTypeGroup.objects.filter(
                transition_type=self.get_object()).values('transition_group')
        ]
        return Response(projects.TransitionGroupSerializer(tgrps, many=True).data)


class TransitionGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionGroup.objects.all()
    serializer_class = projects.TransitionGroupSerializer

    @detail_route(methods=['get'])
    def types(self, *args, **kwargs):
        tts = [
            models.TransitionType.objects.get(pk=obj['transition_type'])
            for obj in models.TransitionTypeGroup.objects.filter(
                transition_group=self.get_object()).values('transition_type')
            ]
        return Response(projects.TransitionTypeSerializer(tts, many=True).data)


class TransitionTypeGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionTypeGroup.objects.all()
    serializer_class = projects.TransitionTypeGroupSerializer


class TransitionMultiplierTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionMultiplierType.objects.all()
    serializer_class = projects.TransitionMultiplierTypeSerializer


class AttributeGroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.AttributeGroup.objects.all()
    serializer_class = projects.AttributeGroupSerializer


class StateAttributeTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.StateAttributeType.objects.all()
    serializer_class = projects.StateAttributeTypeSerializer


class TransitionAttributeTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionAttributeType.objects.all()
    serializer_class = projects.TransitionAttributeTypeSerializer


""" Scenario configuration viewsets """


class DeterministicTransitionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.DeterministicTransition.objects.all()
    serializer_class = scenarios.DeterministicTransitionSerializer


class TransitionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Transition.objects.all()
    serializer_class = scenarios.TransitionSerializer


class InitialConditionsNonSpatialViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.InitialConditionsNonSpatial.objects.all()
    serializer_class = scenarios.InitialConditionsNonSpatialSerializer


class InitialConditionsNonSpatialDistributionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.InitialConditionsNonSpatialDistribution.objects.all()
    serializer_class = scenarios.InitialConditionsNonSpatialDistributionSerializer


class InitialConditionsSpatialViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.InitialConditionsSpatial.objects.all()
    serializer_class = scenarios.InitialConditionsSpatialSerializer


class TransitionTargetViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionTarget.objects.all()
    serializer_class = scenarios.TransitionTargetSerializer


class TransitionMultiplierValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionMultiplierValue.objects.all()
    serializer_class = scenarios.TransitionMultiplierValueSerializer


class TransitionSizeDistributionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionSizeDistribution.objects.all()
    serializer_class = scenarios.TransitionSizeDistributionSerializer


class TransitionSizePrioritizationViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionSizePrioritization.objects.all()
    serializer_class = scenarios.TransitionSizePrioritizationSerializer


class TransitionSpatialMultiplierViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionSpatialMultiplier.objects.all()
    serializer_class = scenarios.TransitionSpatialMultiplierSerializer


class StateAttributeValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.StateAttributeValue.objects.all()
    serializer_class = scenarios.StateAttributeValueSerializer


class TransitionAttributeValueViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionAttributeValue.objects.all()
    serializer_class = scenarios.TransitionAttributeValueSerializer


class TransitionAttributeTargetViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionAttributeTarget.objects.all()
    serializer_class = scenarios.TransitionAttributeTargetSerializer


""" Report viewsets """


class StateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.StateClassSummaryReport.objects.all()
    serializer_class = reports.StateClassSummaryReportSerializer


class TransitionSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionSummaryReport.objects.all()
    serializer_class = reports.TransitionSummaryReportSerializer


class TransitionByStateClassSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionByStateClassSummaryReport.objects.all()
    serializer_class = reports.TransitionByStateClassSummaryReportSerializer


class StateAttributeSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.StateAttributeSummaryReport.objects.all()
    serializer_class = reports.StateAttributeSummaryReportSerializer


class TransitionAttributeSummaryReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransitionAttributeSummaryReport.objects.all()
    serializer_class = reports.TransitionAttributeSummaryReportSerializer


class ReportViewBase(GenericAPIView):
    serializer_class = reports.GenerateReportSerializer

    def _response(self, report):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        config = data['configuration']
        name = config.pop('report_name')
        return self._response(Report(name, config))


class GenerateCSVReportView(ReportViewBase):
    def _response(self, report):
        csv_data = report.get_csv_data()
        response = HttpResponse(content=csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(report.report_name)
        return response


class RequestSpatialDataView(ReportViewBase):
    def _response(self, report):
        return JsonResponse(report.request_zip_data())


class RequestPDFReportView(ReportViewBase):
    def _response(self, report):
        return JsonResponse(report.request_pdf_data())


class RegionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = regions.RegionSerializer

    @detail_route(methods=['get'])
    def reporting_units(self, *args, **kwargs):
        context = {'request': self.request}
        return Response({
            'type': 'FeatureCollection',
            'features': regions.ReportingUnitSerializer(
                self.get_object().reporting_units.all(), many=True, context=context
            ).data
        })


class ReportingUnitViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.ReportingUnit.objects.all()
    serializer_class = regions.ReportingUnitSerializer

