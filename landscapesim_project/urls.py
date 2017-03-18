from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('landscapesim.urls')),
    url(r'^maps/', include('ncdjango.urls'))
]

if settings.DEBUG:
    urlpatterns += [url(r'^$', TemplateView.as_view(template_name='mapviewer.html'))]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)