from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import User, SecretQuestion
from .serializers import UserSerializer, SecretQuestionSerializer, TokenSerializer, PatientSerializer, MedicSerializer
from .tests.utils.mock_decorators import mock_google_user_on_tests
from .utils.google_user import GoogleUser, InvalidTokenException
from .utils.api_mixins import LoggedUserPatchAPIViewMixin, LoggedUserDetailAPIViewMixin


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
        status.HTTP_200_OK: openapi.Response(
            description="User exists.",
            schema=SecretQuestionSerializer(many=True)
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing or Invalid token. Look at the 'error' key on the response to see whether the token is missing or invalid."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Invalid google username."
        ),
        status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
            description="User does not exist.",
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
            questions_serializer = SecretQuestionSerializer(SecretQuestion.objects.order_by('description'), many=True)
            if not google_user.username_is_valid:
                response = Response({'error': 'Invalid User'}, status=status.HTTP_404_NOT_FOUND)
            elif not User.objects.filter(username=google_user.user_id).exists():
                response = Response({'warning': 'User do not exist.', 'questions': questions_serializer.data}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user = User.objects.get(username=google_user.user_id)
                response = Response({'questions': questions_serializer.data, 'user': UserSerializer(user).data},
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
        status.HTTP_200_OK: openapi.Response(
            description="User logged in.",
            schema=TokenSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter, non existent user or non existent question."
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="User is banned (max password attempts exceeded)."
        ),
        status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
            description="Invalid credentials provided."
        )
    })
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@mock_google_user_on_tests
def login(request, google_user_class=GoogleUser):
    # Check that there are no missing parameters
    try:
        google_token = request.data['google_token']
        secret_question_id = int(request.data['secret_question_id'])
        answer = request.data['answer']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    # Check existence of both user and secret question
    google_user = google_user_class(google_token)
    try:
        user = User.objects.get(username=google_user.user_id)
        SecretQuestion.objects.get(id=secret_question_id)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    except SecretQuestion.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_400_BAD_REQUEST)

    # Check user status (active / banned)
    if not user.is_active:
        return Response({'message': 'Your account has been blocked due to many access errors'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check whether the question is correct
    if user.secret_question.id != secret_question_id:
        user.log_invalid_try()
        return Response({'message': 'Invalid username, question or answer'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check whether the password is correct
    if user.check_password(answer):
        auth.authenticate(username=user.username, password=answer)
        token, _ = Token.objects.get_or_create(user=user)
        auth.login(request, user)
        user.log_valid_try()
        return Response({'message': 'Logged in', 'token': token.key}, status=status.HTTP_200_OK)
    else:
        user.log_invalid_try()
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
            'birth_date': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Birth date (yy-mm-dd)."),
            'dni': openapi.Schema(type=openapi.TYPE_INTEGER,
                                  description="Argentinean DNI number."),
            'current_medic': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description="Current medic ID of the patient.")
        },
        required=['google_token', 'birth_date', 'dni']
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="User registrated.",
            schema=TokenSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter or license and current_medic specified at the same time."
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
    birth_date = request.data.get('birth_date', None)
    dni = request.data.get('dni', None)
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
                                                password=answer,
                                                last_name=google_user.last_name,
                                                email=google_user.email,
                                                birth_date=birth_date,
                                                dni=dni,
                                                picture_url=google_user.picture_url,
                                                license=license,
                                                current_medic=current_medic,
                                                secret_question_id=secret_question_id)
        auth.authenticate(username=user_created.username, password=answer)
        token, _ = Token.objects.get_or_create(user=user_created)
        response = Response({'user': UserSerializer(user_created).data, 'token': token.key}, status=status.HTTP_201_CREATED)
    return response


# Patients
class PatientListAPIView(APIView):
    @swagger_auto_schema(
        operation_id='get_related_patients',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Data from patients of the current medic. If used as a patient, return a list containing only its own data.",
                schema=PatientSerializer(many=True),
            )
        }
    )
    def get(self, request):
        return Response(PatientSerializer(request.user.related_patients, many=True).data, status=status.HTTP_200_OK)


class PatientDetailAPIView(APIView):
    @swagger_auto_schema(
        operation_id='get_patient',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=PatientSerializer(),
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Patient not related to the logged in medic."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Patient with the given id not found."
            )
        }
    )
    def get(self, request, pk):
        try:
            patient = User.objects.get(pk=pk)
        except User.DoesNotExist:
            response = Response({'message': 'Patient does not exists'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if patient in request.user.related_patients:
                response = Response(PatientSerializer(patient).data, status=status.HTTP_200_OK)
            else:
                response = Response({'message': 'Patient not related to the logged in medic.'}, status=status.HTTP_401_UNAUTHORIZED)
        finally:
            return response


class CurrentPatientDetailUpdateAPIView(LoggedUserPatchAPIViewMixin, LoggedUserDetailAPIViewMixin):
    serializer_class = PatientSerializer

    @swagger_auto_schema(
        operation_id='get_current_patient',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=PatientSerializer(),
            )
        }
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_id='patch_current_patient',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=PatientSerializer(),
            )
        }
    )
    def patch(self, request):
        return super().patch(request)


# Medics
class MedicListAPIView(generics.ListAPIView):
    queryset = User.objects.medics()
    serializer_class = MedicSerializer


class CurrentMedicDetailUpdateAPIView(LoggedUserPatchAPIViewMixin, LoggedUserDetailAPIViewMixin):
    serializer_class = MedicSerializer

    @swagger_auto_schema(
        operation_id='get_current_medic',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Current medic data",
                schema=MedicSerializer(),
            )
        }
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_id='patch_current_medic',
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Current patient data",
                schema=MedicSerializer(),
            )
        }
    )
    def patch(self, request):
        return super().patch(request)


# Questions. Fixme: remove this view if there is no use for it.
class SecretQuestionAPIView(generics.ListAPIView):
    queryset = SecretQuestion.objects.all()
    serializer_class = SecretQuestionSerializer
    permission_classes = (AllowAny,)
