from rest_framework import serializers
from .models import Medic, Patient


class PatientSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format="%Y-%m-%d")
    finish_date = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Patient
        fields = ('username', 'name', 'last_name', 'start_date', 'finish_date')


class MedicSerializer(serializers.ModelSerializer):
    patients = PatientSerializer(many=True)

    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license', 'patients')
