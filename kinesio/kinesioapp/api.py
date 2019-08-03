from rest_framework import generics, status
from .models import ClinicalHistory, ClinicalSession, Image
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from .utils.download import download


class ClinicalHistoryAPIView(generics.ListCreateAPIView):
    queryset = ClinicalHistory.objects.all()
    serializer_class = ClinicalHistorySerializer

    def list(self, request):
        queryset = self.get_queryset().accessible_by(request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ClinicalSessionAPIView(generics.CreateAPIView):
    serializer_class = ClinicalSessionSerializer


class ImageDetailsAPIView(APIView):
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
                description="Downloads the image. Content type: application/octet-stream"
            ),
        }
    )
    def get(self, request, id):
        try:
            image = Image.objects.get(id=id)
        except Image.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        if not image.can_access(request.user):
            return Response({'message': 'User not authorized to access that image. Only the patient and its medic can access the image.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return download(f'image_{image.pk}.jpg', image.content)


class ImageCreateAPIView(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_id='image_create',
        operation_description="Set 'clinical_session_id' and upload the image as a file under 'content'.",
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Missing or invalid token."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Invalid google username or nonexistent user."
            ),
            status.HTTP_200_OK: openapi.Response(
                description="User exists."
            )
        }
    )
    def post(self, request):
        try:
            clinical_session_id = request.data['clinical_session_id']
        except KeyError:
            return Response({'message': 'Missing clinical_session_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uploaded_file = request.data.get('content')
            content = uploaded_file.read()
        except AttributeError:
            return Response({'message': 'Not possible to read \'content\'. Is it a file?'}, status=status.HTTP_400_BAD_REQUEST)

        image = Image.objects.create(content=content, clinical_session_id=clinical_session_id)

        return Response({'message': 'Image created successfully', 'id': image.id}, status=status.HTTP_201_CREATED)
