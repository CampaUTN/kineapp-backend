from rest_framework import serializers
from .models import ClinicalSession, Image


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id',)


class ClinicalSessionSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClinicalSession
        fields = ('id', 'patient_id', 'date', 'status', 'images')
