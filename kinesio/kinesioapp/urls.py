from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^api/v1/medics/?$', api.MedicsAPIView.as_view(), name='medics')
]

urlpatterns = format_suffix_patterns(urlpatterns)
