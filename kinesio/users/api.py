from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from .models import User, SecretQuestion
from .serializers import UserSerializer, SecretQuestionSerializer
from .tests.utils.mock_decorators import mock_google_user_on_tests
from .utils.google_user import GoogleUser, InvalidTokenException
from rest_framework.authtoken.models import Token


@swagger_auto_schema(
    method='post',
    operation_id='users_exists',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'google_token': openapi.Schema(type=openapi.TYPE_STRING,
                                           description="google token that allows the back-end to obtain: given_name, family_name, iss, sub and email"),
        },
        required=['google_token']
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing or invalid token."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Invalid google username or nonexistent user."
        ),
        status.HTTP_200_OK: openapi.Response(
            description="User exists.",
            schema=SecretQuestionSerializer(many=True)
        )
    }
)
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def users_exists(request):
    try:
        google_token = request.data['google_token']
    except KeyError:
        response = Response({'error': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            google_user = GoogleUser(google_token=google_token)
        except InvalidTokenException:
            response = Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            questions = SecretQuestion.objects.all()
            questions_serializer = SecretQuestionSerializer(questions, many=True)
            if not google_user.username_is_valid:
                response = Response({'error': 'Invalid User'}, status=status.HTTP_404_NOT_FOUND)
            elif not User.objects.filter(username=google_user.user_id).exists():
                response = Response({'warning': 'User do not exist.', 'questions': questions_serializer.data}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user = User.objects.get(username=google_user.user_id)
                user_serializer = UserSerializer(user)
                response = Response({'questions': questions_serializer.data, 'user': user_serializer.data},
                                    status=status.HTTP_200_OK)
    return response


@swagger_auto_schema(
    method='post',
    operation_id='login (2FA)',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_INTEGER),
            'secret_question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'answer': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['username', 'secret_question_id', 'answer']
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing or invalid user id."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Invalid google username or nonexistent user."
        ),
        status.HTTP_200_OK: openapi.Response(
            description="User exists.",
        )})
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@mock_google_user_on_tests
def login(request, google_user_class=GoogleUser):
    try:
        google_token = request.data['google_token']
        secret_question_id = int(request.data['secret_question_id'])
        answer = request.data['answer']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        google_user = google_user_class(google_token)
        user = User.objects.get(username=google_user.user_id)
        SecretQuestion.objects.get(id=secret_question_id)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    except SecretQuestion.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_400_BAD_REQUEST)

    if user.tries >= settings.MAX_PASSWORD_TRIES:
        return Response({'message': 'Your account has been blocked due to many access errors'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.secret_question.id != secret_question_id:
        user.tries = user.tries + 1
        user.save()
        return Response({'message': 'Invalid username, question or answer'}, status=status.HTTP_401_UNAUTHORIZED)
    compare = user.check_password(answer)
    if compare:
        if user.is_active:
            auth.authenticate(username=user.username, password=answer)
            token, _ = Token.objects.get_or_create(user=user)
            auth.login(request, user)
            user.tries = 0
            user.save()
            return Response({'message': 'Logged in', 'token': token.key}, status=status.HTTP_200_OK)
        else:
            user.tries = user.tries + 1
            user.save()
            return Response({'message': 'Invalid username, question or answer'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        user.tries = user.tries + 1
        user.save()
        return Response({'message': 'Invalid username, question or answer'}, status=status.HTTP_406_NOT_ACCEPTABLE)


@swagger_auto_schema(
    method='post',
    operation_id='Register',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        description="""To register any kind of user. If license and current_medic are both null or omitted,
                       the user will be patient. If only current_medic is not null, the usuer will be a patient
                       of that medic. If only the license is not null, the user will be a patient.
                       If you set not-null values to both current_medic and license, the response will be status 400.""",
        properties={
            'google_token': openapi.Schema(type=openapi.TYPE_STRING,
                                           description="google token that allows the back-end to obtain: given_name, family_name, iss, sub and email"),
            'license': openapi.Schema(type=openapi.TYPE_STRING,
                                      description="Medic's license."),
            'current_medic': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description="Current medic ID of the patient.")
        },
        required=['google_token']
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter or license and current_medic specified at the same time."
        ),
        status.HTTP_201_CREATED: openapi.Response(
            description="User registrated."
        )
    }
)
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@mock_google_user_on_tests
def register(request, google_user_class=GoogleUser):
    google_token = request.data.get('google_token', None)
    license = request.data.get('license', None)
    secret_question_id = request.data.get('secret_question_id', None)
    answer = request.data.get('answer', None)
    current_medic = request.data.get('current_medic', None)
    if google_token is None:
        response = Response({'error': 'Missing token'},
                            status=status.HTTP_400_BAD_REQUEST)
    elif license is not None and current_medic is not None:
        response = Response({'error': 'Do not specify current_medic and license at the same time'},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        google_user = google_user_class(google_token)
        user_created = User.objects.create_user(username=google_user.user_id,
                                 first_name=google_user.first_name,
                                 last_name=google_user.last_name,
                                 email=google_user.email,
                                 license=license,
                                 current_medic=current_medic,
                                 secret_question_id=secret_question_id)
        user_created.set_password(answer)
        user_created.save()
        user_serializer = UserSerializer(user_created)
        response = Response({'user': user_serializer.data}, status=status.HTTP_201_CREATED)
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


class SecretQuestionAPIView(generics.ListAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer
    permission_classes = (AllowAny,)
