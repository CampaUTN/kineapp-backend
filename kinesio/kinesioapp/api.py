from rest_framework import generics

from .models import ClinicalHistory, ClinicalSession
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer


class ClinicalHistoryAPIView(generics.ListCreateAPIView):
    queryset = ClinicalHistory.objects.all()
    serializer_class = ClinicalHistorySerializer


class ClinicalSessionAPIView(generics.ListCreateAPIView):
    queryset = ClinicalSession.objects.all()
    serializer_class = ClinicalSessionSerializer
