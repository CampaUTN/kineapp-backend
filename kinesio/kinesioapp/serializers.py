from rest_framework import serializers
from .models import Medic, ClinicalHistory, ClinicalSession, Patient


class MedicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license')


class ClinicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalHistory
        fields = ('date', 'description', 'status', 'medic', 'patient')


class ClinicalSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalSession
        fields = ('date', 'status', 'clinical_history')
