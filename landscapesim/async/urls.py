from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from landscapesim.async.views import RunModelViewset

router = DefaultRouter()
router.register('run-model', RunModelViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]
