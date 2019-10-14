from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from kinesioapp.api import clinical_sessions, images, videos, exercises


urlpatterns = [
    # Web Views
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^logout/?$', views.logout_view, name='logout_view'),
    re_path(r'^secret_questions/?$', views.SecretQuestionView.as_view(), name='secret_questions_view'),
    re_path(r'^no_user/?$', views.NoUserView.as_view(), name='no_user_view'),
    re_path(r'^clinical_history/?$', views.ClinicalHistoryView.as_view(), name='clinical_history_view'),
    re_path(r'^clinical_session/?$', views.ClinicalSessionView.as_view(), name='clinical_session_view'),
    re_path(r'^timelapse/?$', views.TimelapseView.as_view(), name='timelapse_view'),
    re_path(r'^videos/?$', views.PublicVideosView.as_view(), name='videos_view'),
    re_path(r'^routine/?$', views.RoutineView.as_view(), name='routine_view'),

    # API
    re_path(r'^api/v1/clinical_sessions/?$', clinical_sessions.ClinicalSessionAPIView.as_view(), name='clinical_session'),
    re_path(r'^api/v1/clinical_sessions_for_patient/(?P<patient_id>[0-9]+)/?', clinical_sessions.ClinicalSessionsForPatientView.as_view(), name='clinical_sessions_for_patient'),
    re_path(r'^api/v1/clinical_sessions/(?P<id>[0-9]+)/?', clinical_sessions.ClinicalSessionUpdateAPIView.as_view(), name='clinical_session_update'),
    re_path(r'^api/v1/image/?$', images.ImageCreateAPIView.as_view(), name='image_create'),
    re_path(r'^api/v1/image/(?P<id>[0-9]+)/?$', images.ImageDetailsAndDeleteAPIView.as_view(), name='image'),
    re_path(r'^api/v1/image/(?P<patient_id>[0-9]+)/(?P<tag>[a-zA-Z]+)?$', images.ImagesWithTagAPIView.as_view(), name='images_with_tag'),
    re_path(r'^api/v1/video/?$', videos.VideoUploadView.as_view(), name='video_create'),
    re_path(r'^api/v1/video/(?P<id>[0-9]+)/?$', videos.VideoDeleteAPIView.as_view(), name='video_delete'),
    re_path(r'^api/v1/exercise/?$', exercises.ExerciseCreateAPIView.as_view(), name='exercise_create'),
    re_path(r'^api/v1/exercise/(?P<id>[0-9]+)/?$', exercises.ExerciseUpdateAndDeleteAPIView.as_view(), name='exercise'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
