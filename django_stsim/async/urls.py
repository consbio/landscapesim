from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from django_stsim.async.views import RunModelViewset, GenerateReportViewset


router = DefaultRouter()
router.register('run-model', RunModelViewset)
router.register('generate-report', GenerateReportViewset)


urlpatterns = [
    url(r'^', include(router.urls)),
]
