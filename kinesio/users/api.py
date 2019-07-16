from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from .models import User, SecretQuestion
from .serializers import UserSerializer, SecretQuestionSerializer
from .utils.google_user import GoogleUser, InvalidTokenException
from django.utils.datastructures import MultiValueDictKeyError


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def token_google_api_view(request):
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
    queryset = User.objects.patients()
    serializer_class = UserSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.patients()
    serializer_class = UserSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = User.objects.medics()
    serializer_class = UserSerializer


class SecretQuestionAPIView(generics.ListCreateAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer


class SecretQuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def check_answer_view(request):
    try:
        user_id = int(request.data['user_id'])
        secret_question_id = int(request.data['secret_question_id'])
        answer = request.data['answer']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
        SecretQuestion.objects.get(id=secret_question_id)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    except SecretQuestion.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_400_BAD_REQUEST)

    if user.secret_question.id != secret_question_id:
        return Response({'message': 'invalid username, question or answer'}, status=status.HTTP_401_UNAUTHORIZED)

    compare = user.check_password(answer)
    token, _ = Token.objects.get_or_create(user=user)
    if compare:
        authenticate(username=user.username, password=answer)
        return Response({'message': 'Logged in', 'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'invalid username, question or answer'}, status=status.HTTP_401_UNAUTHORIZED)
