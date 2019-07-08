from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import generics
from google.oauth2 import id_token

from .models import Medic, ClinicalHistory, ClinicalSession, Patient, CUser
from .serializers import MedicSerializer, ClinicalHistorySerializer, ClinicalSessionSerializer, PatientSerializer


class GetTokenAPIView(APIView):
    def __missing_field_error(self, field_name):
        return Response({'error': f'Missing field: {field_name} field is empty.'},
                        status=status.HTTP_400_BAD_REQUEST)

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
                                status=status.HTTP_404_NOT_FOUND)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)


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


class TokenGoogleAPIView(APIView):
    def post(self, request):
        google_token = request.POST['google_token']

        try:
            id_info = id_token.verify_oauth2_token(
                google_token,
                request.Request(),
                '1093191472549-9gk2os2g3hm2qa1bhrhr1ab0cl7r5qkb.apps.googleusercontent.com')

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return Response({'error': 'Invalid Issuer'}, status=status.HTTP_404_NOT_FOUND)

            user_id = id_info['sub']

            query_user = CUser.objects.filter(id_google=user_id)
            if query_user.count() < 1:
                return Response({'warning': 'User do not exist.'}, status=status.HTTP_206_PARTIAL_CONTENT)
            else:
                #FIXME Cambiar para que devuelva las preguntas cuando el ISSUE 94 este terminado
                return Response({'questions': 'Saraza!'}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_404_NOT_FOUND)
