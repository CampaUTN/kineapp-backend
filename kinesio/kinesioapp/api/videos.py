from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
from rest_framework.request import HttpRequest

from ..models import Video
from ..serializers import VideoSerializer
from ..utils.api_mixins import GenericDeleteView


class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, JSONParser)  # It works without JSONParser, but drf-yasg fails to build the docs

    @swagger_auto_schema(
        operation_id='video_create',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_FILE, description='Upload the video as a file.'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the video.'),
            },
            required=['content', 'name']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing name or content',
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Video created successfully.",
                schema=VideoSerializer()
            )
        }
    )
    def post(self, request: HttpRequest) -> Response:
        try:
            uploaded_file = request.data.get('content')
            name = request.data.get('name')
        except KeyError:
            return Response({'message': 'Missing or invalid file or name.'}, status=status.HTTP_400_BAD_REQUEST)
        video = Video.objects.create(name=name, content=uploaded_file, medic_id=request.user.id)
        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)


class VideoDeleteAPIView(GenericDeleteView):
    model_class = Video

    @swagger_auto_schema(
        operation_id='video_delete',
        operation_description='You will not be able to delete the video if the logged user is not the owner.',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Video's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to delete that video. Only the owner medic can delete this video."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid video id: Video not found"
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="Image deleted successfully.",
            ),
        }
    )
    def delete(self, request: HttpRequest, id: int) -> Response:
        """ This method exist only to add an '@swagger_auto_schema' annotation """
        return super().delete(request, id)
