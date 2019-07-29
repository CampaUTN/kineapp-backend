from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api
from django.contrib.auth.views import auth_logout

urlpatterns = [
    # Login related views
    re_path(r'^api/v1/user_exists/?$', api.users_exists, name='user_exists'),
    re_path(r'^api/v1/login/?$', api.login, name='login_view'),
    re_path(r'^api/v1/secret_questions/?$', api.SecretQuestionAPIView.as_view(), name='secret_questions'),

    # Registration related views
    re_path(r'^api/v1/registration/?$', api.register, name='registration'),

    # Other views
    re_path(r'^api/v1/medics/?$', api.MedicsAPIView.as_view(), name='medics'),
    re_path(r'^api/v1/patients/?$', api.PatientsAPIView.as_view(), name='patients'),
    re_path(r'^api/v1/patients/(?P<pk>[0-9]+)$', api.PatientDetailAPIView.as_view(), name='patient_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
