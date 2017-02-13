from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from django_stsim.views import LibraryViewset, ProjectViewset, ScenarioViewset

router = DefaultRouter()
router.register('libraries', LibraryViewset)
router.register('projects', ProjectViewset)
router.register('scenarios', ScenarioViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]