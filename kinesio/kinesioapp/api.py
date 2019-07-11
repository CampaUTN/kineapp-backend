from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import generics
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import ClinicalHistory, ClinicalSession

from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer
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

from .models import ClinicalHistory, ClinicalSession
from .serializers import ClinicalHistorySerializer, ClinicalSessionSerializer
from users.models import CustomUser


class ClinicalHistoryAPIView(generics.ListCreateAPIView):
    queryset = ClinicalHistory.objects.all()
    serializer_class = ClinicalHistorySerializer


class ClinicalSessionAPIView(generics.ListCreateAPIView):
    queryset = ClinicalSession.objects.all()
    serializer_class = ClinicalSessionSerializer


class TokenGoogleAPIView(APIView):
    def post(self, request):
        google_token = request.data.get('google_token', None)
        if google_token is None:
            return Response({'error': 'Missing token'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print(google_token)
            try:
                id_info = id_token.verify_oauth2_token(
                    google_token,
                    requests.Request(),
                    '1093191472549-9gk2os2g3hm2qa1bhrhr1ab0cl7r5qkb.apps.googleusercontent.com')

                if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    return Response({'error': 'Invalid Issuer'}, status=status.HTTP_404_NOT_FOUND)

                user_id = id_info['sub']

                query_user = CustomUser.objects.filter(id_google=user_id)
                if query_user.count() > 0:
                    return Response({'warning': 'User do not exist.'}, status=status.HTTP_206_PARTIAL_CONTENT)
                else:
                    # FIXME Cambiar para que devuelva las preguntas cuando el ISSUE 94 este terminado
                    return Response({'questions': 'Saraza!'}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_404_NOT_FOUND)
