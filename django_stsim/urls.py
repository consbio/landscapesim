from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from django_stsim.views import LibraryViewset, ProjectViewset, ScenarioViewset,\
    StratumViewset, StateClassViewset, TransitionTypeViewset,\
    TransitionGroupViewset, TransitionTypeGroupViewset, TransitionViewset, \
    StateClassSummaryReportViewset, TransitionSummaryReportViewset, \
    TransitionByStateClassSummaryReportViewset, RunControlViewset, OutputOptionViewset

router = DefaultRouter()
router.register('libraries', LibraryViewset)
router.register('projects', ProjectViewset)
router.register('scenarios', ScenarioViewset)
router.register('strata', StratumViewset)
router.register('stateclasses', StateClassViewset)
router.register('transition-types', TransitionTypeViewset)
router.register('transition-groups', TransitionGroupViewset)
router.register('transition-type-groups', TransitionTypeGroupViewset)
router.register('transitions', TransitionViewset)
router.register('stateclass-summaries', StateClassSummaryReportViewset)
router.register('transition-summaries', TransitionSummaryReportViewset)
router.register('transition-by-stateclass-summaries', TransitionByStateClassSummaryReportViewset)
router.register('run-controls', RunControlViewset)
router.register('output-options', OutputOptionViewset)


urlpatterns = [
    url(r'^', include(router.urls)),
]