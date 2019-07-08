from rest_framework import generics

from .models import Medic, Patient
from .serializers import MedicSerializer, PatientSerializer


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer
