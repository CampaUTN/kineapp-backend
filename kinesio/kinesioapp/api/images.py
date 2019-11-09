from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.request import HttpRequest

from ..serializers import ThumbnailSerializer
from ..models import Image
from users.models import User
from ..serializers import ImageSerializer
from .. import choices
from ..utils.api_mixins import GenericDeleteView, GenericDetailsView


class ImageDetailsAndDeleteAPIView(GenericDeleteView, GenericDetailsView):
    model_class = Image
    serializer_class = ImageSerializer

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
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access that image. Only the patient and its medic can access the image."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid image id: Image not found"
            ),
            status.HTTP_200_OK: openapi.Response(
                description='Image found and accessible.',
                schema=ImageSerializer()
            ),
        }
    )
    def get(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().get(request, id)

    @swagger_auto_schema(
        operation_id='image_delete',
        operation_description='You will not be able to delete the image if the logged user does not have access.',
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Image's ID.",
                required=True
            ),
        ],
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Invalid parameter',
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access that image. Only the patient and its medic can access the image."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid image id: Image not found"
            ),
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="Image deleted successfully.",
                schema=ThumbnailSerializer()
            ),
        }
    )
    def delete(self, request: HttpRequest, id: int) -> Response:
        # This method exist only to add an '@swagger_auto_schema' annotation
        return super().delete(request, id)


class ImagesWithTagAPIView(APIView):
    @swagger_auto_schema(
        operation_id='images_of_patient',
        operation_description='This method returns the images matching the given patient and tag. You will not get the images if the current user does not have access.',
        manual_parameters=[
            openapi.Parameter(
                name='patient_id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="Patient's ID.",
                required=True
            ),
            openapi.Parameter(
                name='tag', in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Tag (Any of: F, R, L, B, O). You can also use 'A' as a tag to get all images regardless their tags.",
            ),
        ],
        responses={
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authorized to access those images. Only the patient and its medic can access them."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid patient id: Patient not found"
            ),
            status.HTTP_200_OK: openapi.Response(
                description='Images found and accessible.',
                schema=ImageSerializer(many=True)
            ),
        }
    )
    def get(self, request: HttpRequest, patient_id: int, tag: str) -> Response:
        patient = get_object_or_404(User, id=patient_id)
        tag = None if tag.lower() == 'a' else tag
        images = Image.objects.of_patient(patient).by_tag(tag)
        if patient not in request.user.related_patients:
            return Response({'message': 'User not authorized to access those images. Only the patient and its medic can access them.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(ImageSerializer(images, many=True).data, status=status.HTTP_200_OK)


class ImageCreateAPIView(APIView):
    @swagger_auto_schema(
        operation_id='image_create',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'clinical_session_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Image content as base64 string. Be careful to not include extra quotes.'),
                'tag': openapi.Schema(type=openapi.TYPE_STRING, enum=[choices.images.initials()]),
            },
            required=['clinical_session_id', 'content', 'tag']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing or invalid clinical_session_id, tag or content',
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Image created successfully.",
                schema=ThumbnailSerializer()
            )
        }
    )
    def post(self, request: HttpRequest) -> Response:
        try:
            clinical_session_id = request.data['clinical_session_id']
            content_as_base64 = request.data['content']
            tag = request.data['tag']
        except KeyError:
            return Response({'message': 'Missing or invalid clinical_session_id, tag or content.'}, status=status.HTTP_400_BAD_REQUEST)

        content_as_base64 = bytes(content_as_base64, 'utf-8')
        image = Image.objects.create(content_as_base64=content_as_base64, clinical_session_id=clinical_session_id, tag=tag)
        return Response(ThumbnailSerializer(image).data, status=status.HTTP_201_CREATED)
