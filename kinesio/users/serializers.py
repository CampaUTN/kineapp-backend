from rest_framework import serializers
from .models import Medic, Patient, User


class MedicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medic
        fields = ('license',)


class PatientSerializer(serializers.ModelSerializer):
    current_medic_id = serializers.IntegerField()

    class Meta:
        model = Patient
        fields = ('current_medic_id',)


class UserSerializer(serializers.ModelSerializer):
    medic = MedicSerializer()
    patient = PatientSerializer()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'medic', 'patient')

    def _want_to_set_patient_data(self, validated_data):
        return 'patient' in validated_data.keys()

    def _want_to_set_medic_data(self, validated_data):
        return 'medic' in validated_data.keys()

    def _update_user_type(self, instance, validated_data):
        if self._want_to_set_patient_data(validated_data) and self._want_to_set_medic_data(validated_data):
            raise serializers.ValidationError('Do not set medic and patient for the same user')
        elif self._want_to_set_patient_data(validated_data):
            new_medic_id = validated_data.get('patient').get('current_medic_id', None)
            if new_medic_id is not None:
                instance.patient.current_medic = User.objects.get(id=new_medic_id)
        elif self._want_to_set_medic_data(validated_data):
            instance.medic.set_license(validated_data.get('medic').get('license', instance.medic.license))
        else:
            pass

    def update(self, instance, validated_data):
        """
            We need to write a custom 'update' method instead of just setting read_only=True
            because by default the framework will not update nested fields
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        self._update_user_type(instance, validated_data)
        return instance
