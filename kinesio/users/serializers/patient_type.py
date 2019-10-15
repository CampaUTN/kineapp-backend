from rest_framework import serializers

from ..models import Patient
from kinesioapp.serializers import ExerciseSerializer
from .user_medic_lite import MedicUserLiteSerializer


class PatientTypeSerializer(serializers.ModelSerializer):
    current_medic = MedicUserLiteSerializer(read_only=True)
    shared_history_with = MedicUserLiteSerializer(read_only=True, many=True)
    exercises = ExerciseSerializer(read_only=True, many=True)

    class Meta:
        model = Patient
        fields = ('current_medic', 'shared_history_with', 'exercises')

    def update(self, instance: Patient, validated_data: dict):
        if 'current_medic_id' in validated_data and validated_data.get('current_medic_id') is not None and validated_data.get('current_medic_id') <= 0:
            validated_data.update({'current_medic_id': None})
        return super().update(instance, validated_data)

    def to_representation(self, obj: Patient):
        """ Method to return the exercises in a friendly way for the front end """
        data = super().to_representation(obj)
        exercises_per_day = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}  # days from monday (0) to sunday (6).
        for exercise in data['exercises']:
            day = exercise.pop('day')
            exercises_per_day[str(day)].append(exercise)
        data['exercises'] = exercises_per_day
        return data
