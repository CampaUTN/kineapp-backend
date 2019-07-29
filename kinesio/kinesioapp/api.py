from rest_framework import generics, status
from .models import ClinicalHistory, ClinicalSession, Image
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer, ImageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


@api_view(["POST"])
def upload_image(request):
    description = request.data.get('description', '')
    try:
        content = request.data['content']
        date = request.data['date']
        clinical_session_id = request.data['clinical_session_id']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        Image.objects.create(content=content, description=description, date=date,
                             clinical_session_id=clinical_session_id)
    except Exception as e:
        return Response({'message': 'Error: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Image created successfully'}, status=status.HTTP_201_CREATED)


class ImageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
