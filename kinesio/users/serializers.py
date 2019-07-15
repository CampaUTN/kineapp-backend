from rest_framework import serializers
from .models import Medic, Patient, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')


class MedicSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Medic
        fields = ('user', 'license')


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = ('user', 'current_medic_id')
