from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.request import HttpRequest
from django.shortcuts import get_object_or_404

from ..models import User, SecretQuestion
from ..serializers import UserSerializer, TokenSerializer
from ..tests.utils.mock_decorators import mock_google_user_on_tests
from ..utils.google_user import GoogleUser


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
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'secret_question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'answer': openapi.Schema(type=openapi.TYPE_STRING),
            'birth_date': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Birth date (yyyy-mm-dd)."),
            'dni': openapi.Schema(type=openapi.TYPE_INTEGER,
                                  description="Argentinean DNI number."),
            'license': openapi.Schema(type=openapi.TYPE_STRING,
                                      description="Medic's license."),
            'current_medic': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description="Current medic ID of the patient.")
        },
        required=['google_token', 'secret_question_id', 'answer', 'birth_date', 'dni']
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="User registrated.",
            schema=TokenSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter or license and current_medic specified at the same time."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Secret question not found."
        )
    }
)
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@mock_google_user_on_tests
def register(request: HttpRequest, google_user_class: type = GoogleUser) -> Response:
    google_token = request.data.get('google_token')
    secret_question_id = request.data.get('secret_question_id')
    answer = request.data.get('answer')
    license = request.data.get('license')
    current_medic = request.data.get('current_medic')
    if google_token is None or answer is None or secret_question_id is None or answer == '':
        response = Response({'error': 'Missing token, answer, secret_question_id or empty answer'},
                            status=status.HTTP_400_BAD_REQUEST)
    elif license is not None and current_medic is not None:
        response = Response({'error': 'Do not specify current_medic and license at the same time'},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        get_object_or_404(SecretQuestion, id=secret_question_id)  # Check secret question existence
        google_user = google_user_class(google_token)
        user_created = User.objects.create_user(username=google_user.user_id,
                                                first_name=request.data.get('first_name', google_user.first_name),
                                                last_name=request.data.get('last_name', google_user.last_name),
                                                password=answer,
                                                email=google_user.email,
                                                birth_date=request.data.get('birth_date'),
                                                dni=request.data.get('dni'),
                                                _picture_base64=google_user.picture_base64,
                                                license=license,
                                                current_medic=current_medic,
                                                secret_question_id=secret_question_id)
        auth.authenticate(username=user_created.username, password=answer)
        token, _ = Token.objects.get_or_create(user=user_created)
        response = Response({'user': UserSerializer(user_created).data, 'token': token.key}, status=status.HTTP_201_CREATED)
    return response
