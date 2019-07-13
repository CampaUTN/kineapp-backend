from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import CustomUser
from .serializers import CustomUserSerializer
from .utils.google_connector import GoogleConnector, InvalidTokenException
from django.utils.datastructures import MultiValueDictKeyError


class TokenGoogleAPIView(APIView):
    def post(self, request):
        try:
            google_token = request.data['google_token']
        except MultiValueDictKeyError:
            response = Response({'error': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                google_connector = GoogleConnector(google_token=google_token)
            except InvalidTokenException:
                response = Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not google_connector.username_is_valid:
                    response = Response({'error': 'Invalid User'}, status=status.HTTP_404_NOT_FOUND)
                elif CustomUser.objects.filter(id_google=google_connector.user_id).exists():
                    response = Response({'warning': 'User do not exist.'}, status=status.HTTP_206_PARTIAL_CONTENT)
                else:
                    # FIXME Cambiar para que devuelva las preguntas cuando el ISSUE 94 este terminado
                    response = Response({'questions': ['Question 1', 'Question 2', 'Question 3']}, status=status.HTTP_200_OK)
        return response


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.medics()
    serializer_class = CustomUserSerializer
