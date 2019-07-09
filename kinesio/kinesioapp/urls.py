from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^api/v1/clinical_histories/?$', api.ClinicalHistoryAPIView.as_view(), name='clinical_history'),
    re_path(r'^api/v1/clinical_sessions/?$', api.ClinicalSessionAPIView.as_view(), name='clinical_session'),
    re_path(r'^api/v1/login_google/?$', api.TokenGoogleAPIView.as_view(), name='token_google')
]

urlpatterns = format_suffix_patterns(urlpatterns)
