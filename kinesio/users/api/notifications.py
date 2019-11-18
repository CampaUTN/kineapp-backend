from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import HttpRequest

from ..models import User
from rest_framework.views import APIView


class ChangeDeviceIDAPIView(APIView):
    model_class = User

    @swagger_auto_schema(
        operation_id='update_device_id',
        operation_description='Change Firebase\'s device ID for the logged in user',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'firebase_device_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                     description='Device ID to identify the device and send custom notifications to it.'),
            },
            required=['firebase_device_id']
        ),
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Missing device ID.'
            ),
            status.HTTP_202_ACCEPTED: openapi.Response(
                description='Device ID changed.',
            )
        }
    )
    def post(self, request: HttpRequest) -> Response:
        try:
            firebase_device_id = request.data['firebase_device_id']
        except KeyError:
            response = Response({'message': 'Se ha detectado un problema en la conexión a internet. Recuerde que la conexión es importante para el envío de notificaciones.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            request.user.change_firebase_device_id(firebase_device_id)
            response = Response(status=status.HTTP_202_ACCEPTED)
        return response
