from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^logout/?$', views.logout_view, name='logout_view'),
    re_path(r'^secret_questions/?$', views.SecretQuestionView.as_view(), name='secret_questions_view'),
    re_path(r'^no_user/?$', views.NoUserView.as_view(), name='no_user_view'),
    re_path(r'^clinical_history/?$', views.ClinicalHistoryView.as_view(), name='clinical_history_view'),
    re_path(r'^api/v1/clinical_histories/?$', api.ClinicalHistoryAPIView.as_view(), name='clinical_history'),
    re_path(r'^api/v1/clinical_sessions/?$', api.ClinicalSessionAPIView.as_view(), name='clinical_session'),
    re_path(r'^api/v1/image/?$', api.upload_image, name='image'),
    re_path(r'^api/v1/image/(?P<pk>[0-9]+)$', api.ImageDetailAPIView.as_view(), name='image_delete'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
