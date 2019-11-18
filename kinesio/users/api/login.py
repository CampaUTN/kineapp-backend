from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.request import HttpRequest

from ..models import User
from ..serializers import TokenSerializer
from ..tests.utils.mock_decorators import inject_dependencies_on_testing
from ..utils.google_user import GoogleUser, GoogleRejectsTokenException, InformationNotAccessibleFromTokenException, InvalidAudienceException
from ..tests.utils.mocks import GoogleUser as GoogleUserMock
from .utils.authenticate import authenticate


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
            description="Missing parameter, non-integer secret_question_id, error related to google token (see response's message for details)",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                })),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="User is banned (max password attempts exceeded), the question or the answer are invalid."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="User or Secret question not found."
        )
    })
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@inject_dependencies_on_testing({'google_user_class': GoogleUserMock})
def login(request: HttpRequest, google_user_class: type = GoogleUser) -> Response:
    # Check that there are no missing parameters
    try:
        google_token = request.data['google_token']
        secret_question_id = int(request.data['secret_question_id'])
        answer = request.data['answer']
    except KeyError:
        return Response({'message': 'Ha omitido uno o más campos obligatorios. Complételos e intente nuevamente.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check whether google token is valid
    try:
        google_user = google_user_class(google_token)
    except (InformationNotAccessibleFromTokenException, GoogleRejectsTokenException, InvalidAudienceException) as exception:
        return Response({'message': 'Google no nos permite acceder a todos los datos necesarios para permitir el inicio de sesión. Verfique los permisos de acceso a sus datos e intente nuevamente.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        # Check user existence
        user = get_object_or_404(User, username=google_user.user_id)
        return authenticate(request, user, secret_question_id, answer)
