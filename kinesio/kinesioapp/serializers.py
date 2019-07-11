from rest_framework import serializers
from .models import ClinicalHistory, ClinicalSession, SecretQuestion
from users.serializers import PatientSerializer


class ClinicalSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClinicalSession
        fields = ('date', 'status', 'clinical_history')


class ClinicalHistorySerializer(serializers.ModelSerializer):
    clinical_sessions = ClinicalSessionSerializer(many=True, required=False)
    patient_id = serializers.IntegerField(write_only=True)
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = ClinicalHistory 
        fields = ('date', 'description', 'status', 'patient_id', 'patient', 'clinical_sessions')

class SecretQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SecretQuestion
        fields = ('__all__')


