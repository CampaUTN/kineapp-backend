from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

urlpatterns = [
    re_path(r'^api/v1/medics/?$', api.MedicsAPIView.as_view(), name='medics'),
    re_path(r'^api/v1/patients/?$', api.PatientsAPIView.as_view(), name='patients'),
    re_path(r'^api/v1/patients/(?P<pk>[0-9]+)$', api.PatientDetailAPIView.as_view(), name='patient_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
