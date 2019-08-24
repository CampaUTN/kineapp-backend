from rest_framework import serializers
from .models import ClinicalSession, Image


class ImageSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source='content_as_base64', read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'tag', 'content')


class ThumbnailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.CharField(source='thumbnail_as_base64', read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'tag', 'thumbnail')


class ClinicalSessionSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClinicalSession
        fields = ('id', 'patient_id', 'date', 'status', 'images')
