from rest_framework import serializers
from .models import ClinicalHistory, ClinicalSession, Image
from users.serializers import UserSerializer


class ClinicalSessionSerializer(serializers.ModelSerializer):
    clinical_history_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ClinicalSession
        fields = ('date', 'status', 'clinical_history_id')


class ClinicalHistorySerializer(serializers.ModelSerializer):
    clinical_sessions = ClinicalSessionSerializer(many=True, required=False)
    patient_id = serializers.IntegerField(write_only=True)
    patient = UserSerializer(read_only=True)

    class Meta:
        model = ClinicalHistory
        fields = ('date', 'description', 'status', 'patient_id', 'patient', 'clinical_sessions')


class ImageSerializer(serializers.ModelSerializer):
    clinical_session = ClinicalSessionSerializer(required=True)

    class Meta:
        model: Image
        fields = '__all__'
