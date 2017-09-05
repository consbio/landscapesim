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
    urlpatterns += [
        url(r'^basictest/$', TemplateView.as_view(template_name='test.html')),
        url(r'^maptest/$', TemplateView.as_view(template_name='mapviewer.html')),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)