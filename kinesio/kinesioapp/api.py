from rest_framework import generics, status
from .models import ClinicalHistory, ClinicalSession, Image
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer, ImageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView


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


class ImageAPIView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        description = request.data.get('description', '')
        try:
            uploaded_file = request.data.get('content')
            content = uploaded_file.read()
            date = request.data['date']
            clinical_session_id = request.data['clinical_session_id']
        except KeyError:
            return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)
        Image.objects.create(content=content, description=description, date=date,
                             clinical_session_id=clinical_session_id)

        return Response({'message': 'Image created successfully'}, status=status.HTTP_201_CREATED)


class ImageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
