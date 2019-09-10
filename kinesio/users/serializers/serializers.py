from rest_framework import serializers
from ..models import Medic, Patient, User, SecretQuestion
from rest_framework.authtoken.models import Token
from kinesioapp.serializers import ExerciseForDaySerializer

class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key', read_only=True)

    class Meta:
        model = Token
        fields = ('token',)


class MedicTypeSerializer(serializers.ModelSerializer):
    license = serializers.CharField(required=False)  # otherwise the drf-yasg detects it as required

    class Meta:
        model = Medic
        fields = ('license',)


class PatientTypeSerializer(serializers.ModelSerializer):
    current_medic_id = serializers.IntegerField(required=False)  # otherwise the drf-yasg detects it as required
    exercises = ExerciseForDaySerializer(source='exercise_for_day', read_only=True, many=True)

    class Meta:
        model = Patient
        fields = ('current_medic_id', 'videos', 'exercises')  # fixme: remove 'videos' from here, because they are already on the exercises.

    def to_representation(self, obj):
        """ Method to return the exercises in a friendly way for the front end """
        data = super().to_representation(obj)
        exercises_per_day = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}  # days from monday (0) to sunday (6).
        for exercise in data['exercises']:
            exercises_per_day[str(exercise['day'])].append(exercise['exercise'])
        data['exercises'] = exercises_per_day
        return data


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)  # otherwise the drf-yasg detects it as required. fixme: same as password
    is_active = serializers.BooleanField(read_only=True, required=False)
    email = serializers.CharField(read_only=True, required=False)
    # We need the specific fields on the superclass because sometimes we want to return an user but we don't know
    # whether is a patient or a medic. The options are the current one or multiple type tests on different places.
    medic = MedicTypeSerializer(required=False)
    patient = PatientTypeSerializer(required=False)
    password = serializers.CharField(min_length=4,
                                     write_only=True,
                                     required=False,  # otherwise the drf-yasg detects it as required. fixme: change auth method on drf-yasg, because the detection of HTTP Authorization scheme as "basic" is requestion for user and password even if write_only=True.
                                     style={'input_type': 'password'})
    picture_url = serializers.CharField(read_only=True, required=False)
    dni = serializers.IntegerField(required=False)
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'medic', 'patient', 'password',
                  'picture_url', 'dni', 'birth_date')

    def _want_to_set_patient_data(self, validated_data):
        return 'patient' in validated_data.keys()

    def _want_to_set_medic_data(self, validated_data):
        return 'medic' in validated_data.keys()

    def update(self, instance, validated_data):
        # Remove nested field information from validated_data
        medic_data = validated_data.pop('medic') if self._want_to_set_medic_data(validated_data) else None
        patient_data = validated_data.pop('patient') if self._want_to_set_patient_data(validated_data) else None

        # Update User
        super().update(instance, validated_data)

        # Update User's type.
        if patient_data is not None:
            PatientTypeSerializer().update(instance.patient, patient_data)
        elif medic_data is not None:
            MedicTypeSerializer().update(instance.medic, medic_data)
        else:
            pass
        return instance


class PatientSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'is_active', 'patient', 'password',
                  'picture_url', 'dni', 'birth_date')


class MedicSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'is_active', 'medic', 'password',
                  'picture_url', 'dni', 'birth_date')


class SecretQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretQuestion
        fields = '__all__'
