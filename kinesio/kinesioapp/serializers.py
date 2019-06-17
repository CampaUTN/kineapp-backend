from rest_framework import serializers
from .models import Medic


class MedicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license')
