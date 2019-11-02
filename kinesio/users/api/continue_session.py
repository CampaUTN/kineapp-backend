from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import HttpRequest
import textwrap

from ..serializers import TokenSerializer
from .utils.authenticate import authenticate
from ..utils.session_timeout_exempt import session_timeout_exempt
from kinesio.settings import SESSION_TIMEOUT_KEY
import time



@swagger_auto_schema(
    method='post',
    operation_id='continue_session',
    operation_description=textwrap.dedent(""" Similar to login endpoint. However, instead of requesting google's token,
                                              this endpoint requires the user to be logged in.
                                              This is not for login. It's to confirm session validity after the
                                              automatic logout. """),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'secret_question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'answer': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['secret_question_id', 'answer']
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="User session will continue.",
            schema=TokenSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter or non-integer secret_question_id (see response's message for details)",
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
@session_timeout_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def continue_session(request: HttpRequest) -> Response:
    # Check whether there are missing parameters
    try:
        secret_question_id = int(request.data['secret_question_id'])
        answer = request.data['answer']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Update the session timeout time
        request.session[SESSION_TIMEOUT_KEY] = time.time()
        return authenticate(request, request.user, secret_question_id, answer)
