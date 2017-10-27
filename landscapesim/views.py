from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from landscapesim import models
from landscapesim.report import Report
from landscapesim.serializers import projects, reports, scenarios


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


class GeneratePDFReportView(ReportViewBase):
    def _response(self, report):
        pdf_data = report.get_pdf_data()
        response = HttpResponse(content=pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(report.report_name)
        return response


class RequestSpatialDataView(ReportViewBase):
    def _response(self, report):
        return JsonResponse(report.request_zip_data())


# Debugging report and css
from django.views.generic import TemplateView
from landscapesim.report import Report
from landscapesim.models import Scenario
class DebugPDFView(TemplateView):
    template_name = 'pdf/report.html'

    def get(self, request, *args, **kwargs):
        svg_text = '<svg version="1.1" class="highcharts-root" style="font-family:&quot;Lucida Grande&quot;, &quot;Lucida Sans Unicode&quot;, Arial, Helvetica, sans-serif;font-size:12px;" xmlns="http://www.w3.org/2000/svg" width="308" height="250" viewBox="0 0 308 250"><desc>Created with Highcharts 6.0.2</desc><defs><clipPath id="highcharts-eljgc4h-29"><rect x="0" y="0" width="240" height="140" fill="none"></rect></clipPath></defs><rect fill="#ffffff" class="highcharts-background" x="0" y="0" width="308" height="250" rx="0" ry="0"></rect><rect fill="none" class="highcharts-plot-background" x="58" y="10" width="240" height="140"></rect><g class="highcharts-pane-group"></g><rect fill="none" class="highcharts-plot-border" x="58" y="10" width="240" height="140"></rect><g class="highcharts-grid highcharts-xaxis-grid "><path fill="none" class="highcharts-grid-line" d="M 84.5 10 L 84.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 110.5 10 L 110.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 137.5 10 L 137.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 164.5 10 L 164.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 190.5 10 L 190.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 217.5 10 L 217.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 244.5 10 L 244.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 270.5 10 L 270.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 297.5 10 L 297.5 150" opacity="1"></path><path fill="none" class="highcharts-grid-line" d="M 57.5 10 L 57.5 150" opacity="1"></path></g><g class="highcharts-grid highcharts-yaxis-grid "><path fill="none" stroke="#e6e6e6" stroke-width="1" class="highcharts-grid-line" d="M 58 150.5 L 298 150.5" opacity="1"></path><path fill="none" stroke="#e6e6e6" stroke-width="1" class="highcharts-grid-line" d="M 58 103.5 L 298 103.5" opacity="1"></path><path fill="none" stroke="#e6e6e6" stroke-width="1" class="highcharts-grid-line" d="M 58 57.5 L 298 57.5" opacity="1"></path><path fill="none" stroke="#e6e6e6" stroke-width="1" class="highcharts-grid-line" d="M 58 9.5 L 298 9.5" opacity="1"></path></g><g class="highcharts-axis highcharts-xaxis "><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 84.5 150 L 84.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 110.5 150 L 110.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 137.5 150 L 137.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 164.5 150 L 164.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 190.5 150 L 190.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 217.5 150 L 217.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 244.5 150 L 244.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 270.5 150 L 270.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 298.5 150 L 298.5 160" opacity="1"></path><path fill="none" class="highcharts-tick" stroke="#ccd6eb" stroke-width="1" d="M 57.5 150 L 57.5 160" opacity="1"></path><path fill="none" class="highcharts-axis-line" stroke="#ccd6eb" stroke-width="1" d="M 58 150.5 L 298 150.5"></path></g><g class="highcharts-axis highcharts-yaxis "><text x="13.609375" text-anchor="middle" transform="translate(0,0) rotate(270 13.609375 80)" class="highcharts-axis-title" style="color:#666666;fill:#666666;" y="80"><tspan>Percent of Landscape</tspan></text><path fill="none" class="highcharts-axis-line" d="M 58 10 L 58 150"></path></g><g class="highcharts-series-group"><g class="highcharts-series highcharts-series-0 highcharts-column-series highcharts-color-0  highcharts-tracker" transform="translate(58,10) scale(1 1)" clip-path="url(#highcharts-eljgc4h-29)"><rect x="0.5" y="47.5" width="24" height="93" fill="rgb(128,255,128)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="27.5" y="117.5" width="24" height="23" fill="rgb(255,128,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="54.5" y="47.5" width="24" height="93" fill="rgb(255,128,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="80.5" y="140.5" width="24" height="0" fill="rgb(255,255,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="107.5" y="70.5" width="24" height="70" fill="rgb(0,255,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="134.5" y="93.5" width="24" height="47" fill="rgb(0,128,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="160.5" y="140.5" width="24" height="0" fill="rgb(255,255,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="187.5" y="117.5" width="24" height="23" fill="rgb(255,0,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect><rect x="214.5" y="70.5" width="24" height="70" fill="rgb(128,0,0)" stroke="#ffffff" stroke-width="1" class="highcharts-point highcharts-color-0"></rect></g><g class="highcharts-markers highcharts-series-0 highcharts-column-series highcharts-color-0 " transform="translate(58,10) scale(1 1)" clip-path="none"></g><g class="highcharts-series highcharts-series-1 highcharts-errorbar-series highcharts-tracker" transform="translate(58,10) scale(1 1)" clip-path="url(#highcharts-eljgc4h-29)"><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 12.5 46 L 12.5 46 M 12.5 46 L 12.5 46"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 6.5 46.5 L 18.5 46.5 M 6.5 46.5 L 18.5 46.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 39.5 116 L 39.5 116 M 39.5 116 L 39.5 116"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 33.5 116.5 L 45.5 116.5 M 33.5 116.5 L 45.5 116.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 66.5 46 L 66.5 46 M 66.5 46 L 66.5 46"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 60.5 46.5 L 72.5 46.5 M 60.5 46.5 L 72.5 46.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 92.5 140 L 92.5 140 M 92.5 140 L 92.5 140"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 86.5 140.5 L 98.5 140.5 M 86.5 140.5 L 98.5 140.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 119.5 70 L 119.5 70 M 119.5 70 L 119.5 70"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 113.5 70.5 L 125.5 70.5 M 113.5 70.5 L 125.5 70.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 146.5 93 L 146.5 93 M 146.5 93 L 146.5 93"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 140.5 93.5 L 152.5 93.5 M 140.5 93.5 L 152.5 93.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 172.5 140 L 172.5 140 M 172.5 140 L 172.5 140"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 166.5 140.5 L 178.5 140.5 M 166.5 140.5 L 178.5 140.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 199.5 116 L 199.5 116 M 199.5 116 L 199.5 116"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 193.5 116.5 L 205.5 116.5 M 193.5 116.5 L 205.5 116.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g><g class="highcharts-point"><path fill="none" class="highcharts-boxplot-stem" stroke="#000000" stroke-width="1" d="M 226.5 70 L 226.5 70 M 226.5 70 L 226.5 70"></path><path fill="none" class="highcharts-boxplot-whisker" stroke="#000000" stroke-width="1" d="M 220.5 70.5 L 232.5 70.5 M 220.5 70.5 L 232.5 70.5"></path><path fill="none" class="highcharts-boxplot-median" stroke="#000000" stroke-width="2" d="M 0 0"></path></g></g><g class="highcharts-markers highcharts-series-1 highcharts-errorbar-series " transform="translate(58,10) scale(1 1)" clip-path="none"></g></g><text x="154" text-anchor="middle" class="highcharts-title" style="color:#333333;font-size:18px;fill:#333333;" y="24"></text><text x="154" text-anchor="middle" class="highcharts-subtitle" style="color:#666666;fill:#666666;" y="24"></text><g class="highcharts-legend"><rect fill="none" class="highcharts-legend-box" rx="0" ry="0" x="0" y="0" width="8" height="8" visibility="hidden"></rect><g><g></g></g></g><g class="highcharts-axis-labels highcharts-xaxis-labels "><text x="73.92605819768401" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 73.92605819768401 166)" y="166" opacity="1"><tspan>Young:Open C…</tspan><title>Young:Open Canopy</title></text><text x="100.59272486435069" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 100.59272486435069 166)" y="166" opacity="1"><tspan>Shrubs and A…</tspan><title>Shrubs and Annual Grasses:Closed Canopy</title></text><text x="127.25939153101736" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 127.25939153101736 166)" y="166" opacity="1"><tspan>Shrubs Deple…</tspan><title>Shrubs Depleted:Closed Canopy</title></text><text x="153.92605819768403" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 153.92605819768403 166)" y="166" opacity="1"><tspan>Seeded:Open…</tspan><title>Seeded:Open Canopy</title></text><text x="180.59272486435069" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 180.59272486435069 166)" y="166" opacity="1"><tspan>Mid:Open Ca…</tspan><title>Mid:Open Canopy</title></text><text x="207.25939153101737" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 207.25939153101737 166)" y="166" opacity="1"><tspan>Mature:Close…</tspan><title>Mature:Closed Canopy</title></text><text x="233.92605819768403" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 233.92605819768403 166)" y="166" opacity="1"><tspan>Crested Whe…</tspan><title>Crested Wheat Grass:Open Canopy</title></text><text x="260.5927248643507" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 260.5927248643507 166)" y="166" opacity="1"><tspan>Annual Gras…</tspan><title>Annual Grasses:Open Canopy</title></text><text x="287.25939153101734" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0) rotate(-45 287.25939153101734 166)" y="166" opacity="1"><tspan>Annual Gras…</tspan><title>Annual Grasses Mono-specific:Open Canopy</title></text></g><g class="highcharts-axis-labels highcharts-yaxis-labels "><text x="43" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0)" y="154" opacity="1"><tspan>0</tspan></text><text x="43" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0)" y="107" opacity="1"><tspan>0.2</tspan></text><text x="43" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0)" y="61" opacity="1"><tspan>0.4</tspan></text><text x="43" style="color:#666666;cursor:default;font-size:11px;fill:#666666;" text-anchor="end" transform="translate(0,0)" y="14" opacity="1"><tspan>0.6</tspan></text></g></svg>'
        s = Scenario.objects.get(pk=62)
        column_charts = [
            {
                'vegtype': stratum.name,
                'svg': svg_text
            } for stratum in s.project.strata.all()
        ]
        config = {
            'zoom': 11,
            'opacity': 1,
            'bbox': [-116.60960551441471, 42.55790050289854, -116.27533823026967, 42.7996938297675],
            'center': {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-116.4424718723422, 42.67879716633302]
                }
            },
            'basemap': 'http://{s}.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            'scenario_id': 62,
            'stacked_charts': column_charts,
            'column_charts': column_charts
        }
        r = Report('overview', configuration=config)
        return self.render_to_response(r.get_context())






