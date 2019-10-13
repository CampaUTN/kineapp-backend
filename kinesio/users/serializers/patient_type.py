from rest_framework import serializers

from ..models import Patient
from kinesioapp.serializers import ExerciseSerializer


class PatientTypeSerializer(serializers.ModelSerializer):
    current_medic_id = serializers.IntegerField(required=False)  # otherwise the drf-yasg detects it as required
    current_medic_first_name = serializers.CharField(source='current_medic.first_name', read_only=True, required=False)
    current_medic_last_name = serializers.CharField(source='current_medic.last_name', read_only=True, required=False)
    exercises = ExerciseSerializer(read_only=True, many=True)

    class Meta:
        model = Patient
        fields = ('current_medic_id', 'current_medic_first_name', 'current_medic_last_name', 'exercises')

    def update(self, instance, validated_data):
        if 'current_medic_id' in validated_data and validated_data.get('current_medic_id') is not None and validated_data.get('current_medic_id') <= 0:
            validated_data.update({'current_medic_id': None})
        return super().update(instance, validated_data)

    def to_representation(self, obj):
        """ Method to return the exercises in a friendly way for the front end """
        data = super().to_representation(obj)
        exercises_per_day = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}  # days from monday (0) to sunday (6).
        for exercise in data['exercises']:
            day = exercise.pop('day')
            exercises_per_day[str(day)].append(exercise)
        data['exercises'] = exercises_per_day
        return data
