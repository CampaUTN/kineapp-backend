from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
# For the hardcoded image only:
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from .models import Image
from .serializers import ClinicalSessionSerializer, ImageSerializer
from .utils.download import download
from . import choices


class ClinicalSessionAPIView(generics.CreateAPIView):
    serializer_class = ClinicalSessionSerializer


class ImageDetailsAndDeleteAPIView(APIView):
    @swagger_auto_schema(
        operation_id='image_details',
        operation_description='You will not get the image if the current user does not have access.',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Image's ID.",
                required=True
            ),
            openapi.Parameter(
                name='thumbnail',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Set it to true if you want to get the thumbnail instead of the full size image")
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access that image. Only the patient and its medic can access the image."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid image id: Image not found"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Downloads the image. Content type: application/octet-stream"
            ),
        }
    )
    def get(self, request, id):
        try:
            image = Image.objects.get(id=id)
            thumbnail = request.GET.get('thumbnail', 'false').lower() == 'true'
        except Image.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        if not image.can_access(request.user):
            return Response({'message': 'User not authorized to access that image. Only the patient and its medic can access the image.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return download(f'image_{image.pk}.jpg', image.content) if not thumbnail else download(f'thumbnail_{image.pk}.jpg', image.thumbnail)

    @swagger_auto_schema(
        operation_id='image_delete',
        operation_description='You will not be able to delete the image if the current user does not have access.',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Image's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access that image. Only the patient and its medic can access the image."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid image id: Image not found"
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="Image deleted successfully.",
                schema=ImageSerializer()
            ),
        }
    )
    def delete(self, request, id):
        try:
            image = Image.objects.get(id=id)
        except Image.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        if not image.can_access(request.user):
            return Response({'message': 'User not authorized to access that image. Only the patient and its medic can access the image.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        image_data = ImageSerializer(image).data
        image.delete()
        return Response(image_data, status=status.HTTP_204_NO_CONTENT)


class ImageCreateAPIView(APIView):
    parser_classes = (MultiPartParser, JSONParser)

    @swagger_auto_schema(
        operation_id='image_create',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'clinical_session_id': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_FILE),
                'tag': openapi.Schema(type=openapi.TYPE_STRING, enum=[choices.images.initials()]),
            },
            required=['clinical_session_id', 'content', 'tag']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="""Missing or invalid clinical_session_id or tag. Also used for invalid or missing content (image).
                               See the message returned with this status code for details about each case."""
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Image created successfully.",
                schema=ImageSerializer()
            )
        }
    )
    def post(self, request):
        try:
            clinical_session_id = request.data['clinical_session_id']
            tag = request.data['tag']
        except KeyError:
            return Response({'message': 'Missing or invalid clinical_session_id or tag'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uploaded_file = request.data.get('content')
            content = uploaded_file.read()
        except AttributeError:
            return Response({'message': 'Not possible to read \'content\'. Is it a file?'}, status=status.HTTP_400_BAD_REQUEST)

        image = Image.objects.create(content=content, clinical_session_id=clinical_session_id, tag=tag)

        return Response(ImageSerializer(image).data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def image_hardcoded(request, id):
    with open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb') as file:
        content = file.read()
    return download(f'image_{id}.jpg', content)
