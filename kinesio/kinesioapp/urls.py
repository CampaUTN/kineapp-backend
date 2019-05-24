from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path(r'^/?$', views.IndexView.as_view(), name='index')
]

urlpatterns = format_suffix_patterns(urlpatterns)
