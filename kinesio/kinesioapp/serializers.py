from rest_framework import serializers
from .models import ClinicalSession, Image, Video


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
    images = ThumbnailSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClinicalSession
        fields = ('id', 'patient_id', 'date', 'description', 'images')


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'name', 'url_to_stream')
