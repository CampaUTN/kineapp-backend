from rest_framework import serializers
from .models import Medic, ClinicalHistory, ClinicalSession


class MedicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license')


class ClinicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalHistory
        fields = ('date', 'description', 'status', 'medic')


class ClinicalSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalSession
        fields = ('medic', 'date', 'status', 'clinical_history')
