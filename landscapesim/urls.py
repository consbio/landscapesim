from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from landscapesim import views

# Initialize routing
router = DefaultRouter()

# Top-level
router.register('libraries', views.LibraryViewset)

# Project definitions
router.register('projects', views.ProjectViewset)
router.register('strata', views.StratumViewset)
router.register('secondary-strata', views.SecondaryStratumViewset)
router.register('stateclasses', views.StateClassViewset)
router.register('transition-types', views.TransitionTypeViewset)
router.register('transition-groups', views.TransitionGroupViewset)
router.register('transition-type-groups', views.TransitionTypeGroupViewset)
router.register('transition-multiplier-types', views.TransitionMultiplierTypeViewset)
router.register('attribute-groups', views.AttributeGroupViewset)
router.register('state-attribute-types', views.StateAttributeTypeViewset)
router.register('transition-attribute-types', views.TransitionAttributeTypeViewset)

# Scenario configurations
router.register('scenarios', views.ScenarioViewset)
router.register('transitions', views.TransitionViewset)
router.register('deterministic-transitions', views.DeterministicTransitionViewset)
router.register('initial-conditions-non-spatial-settings', views.InitialConditionsNonSpatialViewset)
router.register('initial-conditions-non-spatial-distributions', views.InitialConditionsNonSpatialDistributionViewset)
router.register('transition-targets', views.TransitionTargetViewset)
router.register('transition-multiplier-values', views.TransitionMultiplierValueViewset)
router.register('transition-spatial-multipliers', views.TransitionSpatialMultiplierViewset)
router.register('transition-size-distributions', views.TransitionSizeDistributionViewset)
router.register('transition-size-prioritizations', views.TransitionSizePrioritizationViewset)
router.register('state-attribute-values', views.StateAttributeValueViewset)
router.register('transition-attribute-values', views.TransitionAttributeValueViewset)
router.register('transition-attribute-targets', views.TransitionAttributeTargetViewset)
router.register('scenario-output-services', views.ScenarioOutputServicesViewset)

# Reports
router.register('stateclass-summaries', views.StateClassSummaryReportViewset)
router.register('transition-summaries', views.TransitionSummaryReportViewset)
router.register('transition-by-stateclass-summaries', views.TransitionByStateClassSummaryReportViewset)
router.register('state-attribute-summaries', views.StateAttributeSummaryReportViewset)
router.register('transition-attribute-summaries', views.TransitionAttributeSummaryReportViewset)

# Exported url paths
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^jobs/', include('landscapesim.async.urls'))
]
