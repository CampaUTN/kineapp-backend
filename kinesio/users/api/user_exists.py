from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import HttpRequest

from ..models import User, SecretQuestion
from ..serializers import UserSerializer, SecretQuestionSerializer
from ..utils.google_user import GoogleUser, GoogleRejectsTokenException, InformationNotAccessibleFromTokenException, InvalidAudienceException


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
def users_exists(request: HttpRequest) -> Response:
    try:
        google_token = request.data['google_token']
    except KeyError:
        response = Response({'error': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            google_user = GoogleUser(google_token=google_token)
        except InformationNotAccessibleFromTokenException:
            response = Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_400_BAD_REQUEST)
        except GoogleRejectsTokenException:
            response = Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidAudienceException:
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
