from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api, views

web_url_patterns = [
    re_path(r'^logout/?$', views.logout_view, name='logout_view'),
    re_path(r'^secret_questions/?$', views.SecretQuestionView.as_view(), name='secret_questions_view'),
    re_path(r'^continue_session/?$', views.continue_session_view, name='continue_session_view'),
    re_path(r'^no_user/?$', views.NoUserView.as_view(), name='no_user_view'),
]

api_url_patterns = [
    # Login related views
    re_path(r'^api/v1/user_exists/?$', api.users_exists, name='user_exists'),
    re_path(r'^api/v1/login/?$', api.login, name='login'),
    re_path(r'^api/v1/continue_session/?$', api.continue_session, name='continue_session'),
    re_path(r'^api/v1/secret_questions/?$', api.SecretQuestionAPIView.as_view(), name='secret_questions'),

    # Registration related views
    re_path(r'^api/v1/registration/?$', api.register, name='registration'),

    # Medics
    re_path(r'^api/v1/medics/?$', api.MedicListAPIView.as_view(), name='medics'),
    re_path(r'^api/v1/medics/detail/?', api.CurrentMedicDetailUpdateAPIView.as_view(), name='current_medic_detail'),

    # Patients
    re_path(r'^api/v1/patients/?$', api.RelatedPatientsOfMedicAPIView.as_view(), name='related_patients_of_medic'),
    re_path(r'^api/v1/patients/detail/?', api.CurrentPatientDetailUpdateAPIView.as_view(), name='current_patient_detail'),

    # Sharing
    re_path(r'^api/v1/share_sessions/?$', api.share_sessions, name='share_sessions'),
    re_path(r'^api/v1/unshare_sessions/?$', api.unshare_sessions, name='unshare_sessions'),
]

urlpatterns = format_suffix_patterns(web_url_patterns + api_url_patterns)
