from rest_framework import generics

from .models import CustomUser
from .serializers import MedicSerializer, PatientSerializer


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = PatientSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = PatientSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.medics()
    serializer_class = MedicSerializer
