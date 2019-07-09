from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import generics

from .models import Medic, ClinicalHistory, ClinicalSession, Patient, SecretQuestion, SecretAnswer
from .serializers import MedicSerializer, ClinicalHistorySerializer, ClinicalSessionSerializer, PatientSerializer, SecretQuestionSerializer, SecretAnswerSerializer
from simplecrypt import encrypt, decrypt
import logging

class Errors(object):

    @staticmethod
    def missing_field_error(field_name):
        return Response({'error': f'Missing field: {field_name} field is empty.'},
                        status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def is_invalid(field):
        return field is None or field == ''

class GetTokenAPIView(APIView):
    def __missing_field_error(self, field_name):
        return Response({'error': f'Missing field: {field_name} field is empty.'},
                        status=HTTP_400_BAD_REQUEST)

    def __is_invalid(self, field):
        return field is None or field == ''

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if self.__is_valid(username):
            return self.__missing_field_error('username')
        elif self.__is_valid(password):
            return self.__missing_field_error('username')
        else:
            user = authenticate(username=username, password=password)
            if not user:
                return Response({'error': 'Invalid Credentials: Provided credentials are invalid.'},
                                status=HTTP_404_NOT_FOUND)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer


class ClinicalHistoryAPIView(generics.ListCreateAPIView):
    queryset = ClinicalHistory.objects.all()
    serializer_class = ClinicalHistorySerializer


class ClinicalSessionAPIView(generics.ListCreateAPIView):
    queryset = ClinicalSession.objects.all()
    serializer_class = ClinicalSessionSerializer


class SecretQuestionAPIView(generics.ListCreateAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer


class SecretAnswerAPIView(generics.ListCreateAPIView):
    queryset = SecretAnswer.objects.all()
    serializer_class = SecretAnswerSerializer


class CheckAnswerAPIView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id', None)
        answer = request.data.get('answer', None)
        if Errors.is_invalid(user_id):
            return Errors.missing_field_error('user_id')
        elif Errors.is_invalid(answer):
            return Errors.missing_field_error('answer')
        else:
            storedSecretAnswer = SecretAnswerSerializer(SecretAnswer.objects.filter(medic_id=user_id).order_by('-id')[:1]).data
            #print(dir(storedSecretAnswer))
            print(storedSecretAnswer.id)
            #ciphertext = decrypt('s3cr3t', storedSecretAnswer['answer'])

            return Response({'Status': 'a'}, status=HTTP_200_OK)

