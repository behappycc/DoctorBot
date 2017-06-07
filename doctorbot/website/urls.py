from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from website import views

urlpatterns = [
    url(r'^$', views.index_view),
    url(r'^query',views.query,name='query'),
    url(r'^ms_api',views.ms_api,name='ms_api'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
