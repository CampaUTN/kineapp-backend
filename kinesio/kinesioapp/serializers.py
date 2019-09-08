from rest_framework import serializers
from .models import ClinicalSession, Image, Video, Exercise, ExerciseForDay


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
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Video
        fields = ('id', 'name', 'url')


class ExerciseSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    video_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Exercise
        fields = ('id', 'name', 'description', 'video', 'video_id')


class ExerciseForDaySerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = ExerciseForDay
        fields = ('exercise', 'day')
