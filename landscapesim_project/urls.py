from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('landscapesim.urls')),
    url(r'^maps/', include('ncdjango.urls'))
]

if settings.DEBUG:
    from django.views.generic import TemplateView
    urlpatterns += [
        url(r'^basictest/$', TemplateView.as_view(template_name='test.html')),
        url(r'^maptest/$', TemplateView.as_view(template_name='mapviewer.html')),
        url(r'^$', TemplateView.as_view(template_name='index.html'))
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)