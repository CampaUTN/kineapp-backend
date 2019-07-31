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
        patients = [request.user] if request.user.is_patient else request.user.patients.values_list('user')
        queryset = self.get_queryset().filter(patient__in=patients)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ClinicalSessionAPIView(generics.CreateAPIView):
    serializer_class = ClinicalSessionSerializer


class ImageAPIView(generics.DestroyAPIView):
    queryset = Image.objects.all()
    parser_classes = (MultiPartParser,)

    def get(self, request, pk):
        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        return download(f'image_{image.pk}.jpg', image.content)

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
