from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve


DEBUG_ID = getattr(settings, 'DEBUG_ID', 'null')


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['debug_id'] = DEBUG_ID
        return data


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('landscapesim.urls')),
    url(r'^maps/', include('ncdjango.urls')),
    url(r'^$', IndexView.as_view()),
    url(r'^downloads/(?P<path>.*)$', serve, {'document_root': settings.DATASET_DOWNLOAD_DIR})
]

if settings.DEBUG:
    # Use Django to serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
