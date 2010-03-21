from django.http import HttpResponse
from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^lib/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_DIR + '/lib'}),
    (r'^wui/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_DIR + '/src/js'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    # Apps
    (r'^', include('wui.api.urls')),    
    #(r'^admin/', include(admin.site.urls)),
)
