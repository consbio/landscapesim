from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('landscapesim.urls')),
    url(r'^maps/', include('ncdjango.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # In production, we setup DATASET_DOWNLOAD_DIR to point to /tmp and setup the server to direct /downloads/<*.zip> requests locally.
    from django.views.static import serve
    urlpatterns += [
        url(r'^downloads/(?P<path>.*)$', serve, {'document_root': settings.DATASET_DOWNLOAD_DIR})
    ]

    from landscapesim.views import DebugPDFView
    urlpatterns += [
        url(r'^debugpdf/', DebugPDFView.as_view())
    ]
