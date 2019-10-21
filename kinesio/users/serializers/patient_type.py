from rest_framework import serializers
from django.db import transaction

from ..models import User, Patient
from kinesioapp.serializers import ExerciseSerializer
from .user_medic_lite import MedicUserLiteSerializer


class PatientTypeSerializer(serializers.ModelSerializer):
    current_medic = MedicUserLiteSerializer(required=False)
    shared_history_with = MedicUserLiteSerializer(read_only=True, many=True)
    exercises = ExerciseSerializer(read_only=True, many=True)

    class Meta:
        model = Patient
        fields = ('current_medic', 'shared_history_with', 'exercises')

    def update(self, instance: Patient, validated_data: dict):
        if validated_data.get('current_medic', None):
            with transaction.atomic():
                new_medic_id = validated_data.pop('current_medic').get('id', instance.current_medic.id if instance.current_medic else 0)
                new_medic = User.objects.get(id=new_medic_id) if new_medic_id > 0 else None
                if new_medic != instance.current_medic:  # The patient changed or unassigned the medic
                    instance.exercises.all().delete()  # Remove exercises created by the previous medic
                    instance.current_medic = new_medic
        return super().update(instance, validated_data)

    def to_representation(self, obj: Patient):
        """ Method to return the exercises in a friendly way for the front end """
        representation = super().to_representation(obj)
        exercises_per_day = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}  # days from monday (0) to sunday (6).
        for exercise in representation['exercises']:
            day = exercise.pop('day')
            exercises_per_day[str(day)].append(exercise)
        representation['exercises'] = exercises_per_day
        return representation
