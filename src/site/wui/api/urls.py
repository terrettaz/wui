from django.conf.urls.defaults import *
from wui.api.views import *

urlpatterns = patterns('',
    url(r'^$', index, name='api-index'),
    url(r'^ns/(?P<ns>.+)/$', doc_namespace, name='api-namespace'),
    url(r'^(?P<ns>.*)-(?P<cls>.+)/$', doc_class, name='api-class'),
    url(r'^countries/$', countries_json, name='api-countries'),
    
    url(r'^dl/$', download, name='api-download'),
)
