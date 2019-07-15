from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import User, Patient, Medic
from .serializers import UserSerializer, PatientSerializer, MedicSerializer
from .utils.google_user import GoogleUser, InvalidTokenException
from django.utils.datastructures import MultiValueDictKeyError


class TokenGoogleAPIView(APIView):
    def post(self, request):
        try:
            google_token = request.data['google_token']
        except MultiValueDictKeyError:
            response = Response({'error': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                google_user = GoogleUser(google_token=google_token)
            except InvalidTokenException:
                response = Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not google_user.username_is_valid:
                    response = Response({'error': 'Invalid User'}, status=status.HTTP_404_NOT_FOUND)
                elif User.objects.filter(id_google=google_user.user_id).exists():
                    response = Response({'warning': 'User do not exist.'}, status=status.HTTP_206_PARTIAL_CONTENT)
                else:
                    # FIXME Cambiar para que devuelva las preguntas cuando el ISSUE 94 este terminado
                    response = Response({'questions': ['Question 1', 'Question 2', 'Question 3']}, status=status.HTTP_200_OK)
        return response


class RegisterUserAPIView(APIView):
    @staticmethod
    def _get_google_user(google_token):
        """ This method is here to be patched with a mock a GoogleUser while testing """
        return GoogleUser(google_token)

    def post(self, request):
        google_token = request.data.get('google_token', None)
        license = request.data.get('license', None)
        current_medic = request.data.get('current_medic', None)
        if google_token is None:
            response = Response({'error': 'Missing token'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif license is not None and current_medic is not None:
            response = Response({'error': 'Do not specify current_medic and license at the same time'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            google_user = RegisterUserAPIView._get_google_user(google_token=google_token)
            User.objects.create_user(username=google_user.user_id,
                                     first_name=google_user.first_name,
                                     last_name=google_user.last_name,
                                     email=google_user.email,
                                     license=license,
                                     current_medic=current_medic)
            response = Response(status=status.HTTP_201_CREATED)
        return response


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer
