from rest_framework import serializers
from .models import Medic, Patient, CustomUser, CustomUserType, SecretQuestion


class MedicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medic
        fields = ('license',)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('current_medic_id',)


class CustomUserTypeSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    medic = MedicSerializer()

    class Meta:
        model = CustomUserType
        fields = ('patient', 'medic')


class CustomUserSerializer(serializers.ModelSerializer):
    user_type = CustomUserTypeSerializer()

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'user_type')

class SecretQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SecretQuestion
        fields = ('__all__')

