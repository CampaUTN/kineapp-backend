from rest_framework import serializers
from .models import Medic, Patient, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')


class MedicSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Medic
        fields = ('user', 'license')


class PatientSerializer(serializers.ModelSerializer):
    current_medic = CustomUserSerializer()
    user = CustomUserSerializer()

    class Meta:
        model = Patient
        fields = ('user', 'current_medic')
