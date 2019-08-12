from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api

urlpatterns = [
    # Web Views
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^logout/?$', views.logout_view, name='logout_view'),
    re_path(r'^secret_questions/?$', views.SecretQuestionView.as_view(), name='secret_questions_view'),
    re_path(r'^no_user/?$', views.NoUserView.as_view(), name='no_user_view'),
    re_path(r'^clinical_history/?$', views.ClinicalHistoryView.as_view(), name='clinical_history_view'),
    re_path(r'^clinical_session/?$', views.ClinicalSessionView.as_view(), name='clinical_session_view'),

    # API
    re_path(r'^api/v1/clinical_sessions/?$', api.ClinicalSessionAPIView.as_view(), name='clinical_session'),
    re_path(r'^api/v1/image/?$', api.ImageCreateAPIView.as_view(), name='image_create'),
    re_path(r'^api/v1/image/(?P<id>[0-9]+)/?$', api.ImageDetailsAndDeleteAPIView.as_view(), name='image'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
