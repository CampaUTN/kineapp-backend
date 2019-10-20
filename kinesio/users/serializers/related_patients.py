from rest_framework import serializers

from ..models import User
from .user import PatientUserSerializer


class RelatedPatientsSerializer(serializers.ModelSerializer):
    """ Serializes Users with Medic type. Not patients. """
    patients = PatientUserSerializer(many=True, read_only=True, source='medic.related_patients')
    #non_assigned_patients = PatientUserSerializer(many=True, read_only=True, source='shared')
    non_assigned_patients = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('patients', 'non_assigned_patients')

    def get_non_assigned_patients(self, obj: User):
        return [PatientUserSerializer(patient.user).data for patient in obj.shared.all()]

    def to_representation(self, obj: User) -> dict:
        """ Validate that the user is a medic and not a patient. """
        if not obj.is_medic:
            raise serializers.DjangoValidationError('Only users of medic type are serializable with RelatedPatientsSerializer class.')
        return super().to_representation(obj)
