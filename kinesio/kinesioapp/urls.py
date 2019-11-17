from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api


web_url_patterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^clinical_history/?$', views.ClinicalHistoryView.as_view(), name='clinical_history_view'),
    re_path(r'^clinical_session/?$', views.ClinicalSessionView.as_view(), name='clinical_session_view'),
    re_path(r'^timelapse/?$', views.TimelapseView.as_view(), name='timelapse_view'),
    re_path(r'^videos/?$', views.PublicVideosView.as_view(), name='videos_view'),
    re_path(r'^routine/?$', views.RoutineView.as_view(), name='routine_view'),
]

api_url_patterns = [
    # Clinical Sessions
    re_path(r'^api/v1/clinical_sessions/?$', api.ClinicalSessionAPIView.as_view(), name='clinical_session'),
    re_path(r'^api/v1/clinical_sessions_for_patient/(?P<patient_id>[0-9]+)/?', api.ClinicalSessionsForPatientView.as_view(), name='clinical_sessions_for_patient'),
    re_path(r'^api/v1/clinical_sessions/(?P<id>[0-9]+)/?', api.ClinicalSessionUpdateAndDeleteAPIView.as_view(), name='clinical_session_update_and_delete'),

    # Images
    re_path(r'^api/v1/image/?$', api.ImageCreateAPIView.as_view(), name='image_create'),
    re_path(r'^api/v1/image/(?P<id>[0-9]+)/?$', api.ImageDetailsAndDeleteAPIView.as_view(), name='image'),
    re_path(r'^api/v1/image/of_session/(?P<session_id>[0-9]+)/?$', api.ImagesOfClinicalSessionAPIView.as_view(), name='images_of_session'),
    re_path(r'^api/v1/image/(?P<patient_id>[0-9]+)/(?P<tag>[a-zA-Z]+)/?$', api.ImagesWithTagAPIView.as_view(), name='images_with_tag'),

    # Videos
    re_path(r'^api/v1/video/?$', api.VideoUploadView.as_view(), name='video_create'),
    re_path(r'^api/v1/video/(?P<id>[0-9]+)/?$', api.VideoDeleteAPIView.as_view(), name='video_delete'),

    # Exercises
    re_path(r'^api/v1/exercise/?$', api.ExerciseCreateAPIView.as_view(), name='exercise_create'),
    re_path(r'^api/v1/exercise/(?P<id>[0-9]+)/?$', api.ExerciseUpdateAndDeleteAPIView.as_view(), name='exercise'),
]

urlpatterns = format_suffix_patterns(web_url_patterns + api_url_patterns)
