from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

urlpatterns = [
    re_path(r'^api/v1/login_google/?$', api.TokenGoogleAPIView.as_view(), name='login_google'),
    re_path(r'^api/v1/registration_google/?$', api.RegisterUserAPIView.as_view(), name='registration_google'),
    re_path(r'^api/v1/medics/?$', api.MedicsAPIView.as_view(), name='medics'),
    re_path(r'^api/v1/patients/?$', api.PatientsAPIView.as_view(), name='patients'),
    re_path(r'^api/v1/patients/(?P<pk>[0-9]+)$', api.PatientDetailAPIView.as_view(), name='patient_detail'),
    re_path(r'^api/v1/secret_questions/?$', api.SecretQuestionAPIView.as_view(), name='secret_questions'),
    re_path(r'^api/v1/secret_questions/(?P<pk>[0-9]+)$', api.SecretQuestionDetailAPIView.as_view(), name='secret_questions'),
    re_path(r'^api/v1/login_secret_answer/?$', api.Login.as_view(), name='login_secret_question'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
