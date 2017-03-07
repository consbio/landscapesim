from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

# Top-level and project viewsets
from landscapesim.views import LibraryViewset, ProjectViewset, ScenarioViewset,\
    StratumViewset, SecondaryStratumViewset, StateClassViewset, TransitionTypeViewset,\
    TransitionGroupViewset, TransitionTypeGroupViewset, TransitionMultiplierTypeViewset, \
    AttributeGroupViewset, StateAttributeTypeViewset, TransitionAttributeTypeViewset

# Scenario viewsets
from landscapesim.views import DeterministicTransitionViewset, TransitionViewset, InitialConditionsNonSpatialViewset, \
    InitialConditionsNonSpatialDistributionViewset, TransitionTargetViewset, TransitionMultiplierValueViewset, \
    TransitionSizeDistributionViewset, TransitionSizePrioritizationViewset, StateAttributeValueViewset, \
    TransitionAttributeValueViewset, TransitionAttributeTargetViewset

# Report viewsets
from landscapesim.views import \
    StateClassSummaryReportViewset, TransitionSummaryReportViewset, \
    TransitionByStateClassSummaryReportViewset, StateAttributeSummaryReportViewset, \
    TransitionAttributeSummaryReportViewset


# Initialize routing
router = DefaultRouter()

# Top-level
router.register('libraries', LibraryViewset)

# Project definitions
router.register('projects', ProjectViewset)
router.register('strata', StratumViewset)
router.register('secondary-strata', SecondaryStratumViewset)
router.register('stateclasses', StateClassViewset)
router.register('transition-types', TransitionTypeViewset)
router.register('transition-groups', TransitionGroupViewset)
router.register('transition-type-groups', TransitionTypeGroupViewset)
router.register('transition-multiplier-types', TransitionMultiplierTypeViewset)
router.register('attribute-groups', AttributeGroupViewset)
router.register('state-attribute-types', StateAttributeTypeViewset)
router.register('transition-attribute-types', TransitionAttributeTypeViewset)

# Scenario configurations
router.register('scenarios', ScenarioViewset)
router.register('transitions', TransitionViewset)
router.register('deterministic-transitions', DeterministicTransitionViewset)
router.register('initial-conditions-non-spatial-settings', InitialConditionsNonSpatialViewset)
router.register('initial-conditions-non-spatial-distributions', InitialConditionsNonSpatialDistributionViewset)
router.register('transition-targets', TransitionTargetViewset)
router.register('transition-multiplier-values', TransitionMultiplierValueViewset)
router.register('transition-size-distributions', TransitionSizeDistributionViewset)
router.register('transition-size-prioritizations', TransitionSizePrioritizationViewset)
router.register('state-attribute-values', StateAttributeValueViewset)
router.register('transition-attribute-values', TransitionAttributeValueViewset)
router.register('transition-attribute-targets', TransitionAttributeTargetViewset)

# Reports
router.register('stateclass-summaries', StateClassSummaryReportViewset)
router.register('transition-summaries', TransitionSummaryReportViewset)
router.register('transition-by-stateclass-summaries', TransitionByStateClassSummaryReportViewset)
router.register('state-attribute-summaries', StateAttributeSummaryReportViewset)
router.register('transition-attribute-summaries', TransitionAttributeSummaryReportViewset)

# Exported url paths
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^jobs/', include('landscapesim.async.urls'))
]