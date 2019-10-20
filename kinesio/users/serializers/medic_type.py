from rest_framework import serializers

from ..models import Medic
from kinesioapp.serializers import VideoSerializer


class MedicTypeSerializer(serializers.ModelSerializer):
    license = serializers.CharField(required=False)  # otherwise the drf-yasg detects it as required
    videos = VideoSerializer(many=True)

    class Meta:
        model = Medic
        fields = ('license', 'videos')
