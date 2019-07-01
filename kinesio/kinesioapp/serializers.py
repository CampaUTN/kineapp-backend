from rest_framework import serializers
from .models import Medic, ClinicalHistory, ClinicalSession, Patient


class PatientSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format="%Y-%m-%d")
    finish_date = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Patient
        fields = ('username', 'name', 'last_name', 'start_date', 'finish_date')


class MedicSerializer(serializers.ModelSerializer):
    patients = PatientSerializer(many=True, required=False)

    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license', 'patients')


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
