from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.request import HttpRequest

from ..models import User
from ..serializers import UserSerializer


@swagger_auto_schema(
    method='post',
    operation_id='share',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_to_share_with': openapi.Schema(type=openapi.TYPE_INTEGER)
        },
        required=['user_to_share_with']
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Successful share.",
            schema=UserSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter, user_to_share_with",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                })),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="User is not logged."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="User to share with not found."
        )
    })
@api_view(["POST"])
def share_sessions(request: HttpRequest) -> Response:
    try:
        patient = request.user.patient
        id_to_share_with = request.data['user_to_share_with']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    if patient.current_medic and patient.current_medic.id == id_to_share_with:
        return Response({'message': 'You are trying to share with your actual medic'}, status=status.HTTP_400_BAD_REQUEST)

    user_to_share_with = get_object_or_404(User, id=id_to_share_with)
    patient.share_with(user_to_share_with)
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_id='unshare',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_to_unshare_with': openapi.Schema(type=openapi.TYPE_INTEGER)
        },
        required=['user_to_unshare_with']
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Successful unshare.",
            schema=UserSerializer(),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Missing parameter, user_to_unshare_with",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                })),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="User is not logged."
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="User to unshare with not found."
        )
    })
@api_view(["POST"])
def unshare_sessions(request: HttpRequest) -> Response:
    try:
        patient = request.user.patient
        id_to_unshare_with = request.data['user_to_unshare_with']
    except KeyError:
        return Response({'message': 'Missing parameter'}, status=status.HTTP_400_BAD_REQUEST)

    user_to_unshare_with = get_object_or_404(User, id=id_to_unshare_with)
    patient.unshare_with(user_to_unshare_with)
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
