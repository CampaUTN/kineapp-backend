from rest_framework import serializers
from .models import ClinicalHistory, ClinicalSession, Image
from users.serializers import UserSerializer


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id',)


class ClinicalSessionSerializer(serializers.ModelSerializer):
    clinical_history_id = serializers.IntegerField(write_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalSession
        fields = ('id', 'date', 'status', 'clinical_history_id', 'images')


class ClinicalHistorySerializer(serializers.ModelSerializer):
    clinical_sessions = ClinicalSessionSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    patient = UserSerializer(read_only=True)

    class Meta:
        model = ClinicalHistory
        fields = ('id', 'date', 'description', 'status', 'patient_id', 'patient', 'clinical_sessions')
