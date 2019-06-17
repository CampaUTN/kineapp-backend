from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .models import Medic
from .serializers import MedicSerializer


class GetTokenAPIView(APIView):
    def __missing_field_error(self, field_name):
        return Response({'error': f'Missing field: {field_name} field is empty.'},
                        status=HTTP_400_BAD_REQUEST)

    def __is_invalid(self, field):
        return field is None or field == ''

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if self.__is_valid(username):
            return self.__missing_field_error('username')
        elif self.__is_valid(password):
            return self.__missing_field_error('username')
        else:
            user = authenticate(username=username, password=password)
            if not user:
                return Response({'error': 'Invalid Credentials: Provided credentials are invalid.'},
                                status=HTTP_404_NOT_FOUND)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)


class MedicsAPIView(APIView):
    def get(self, request):
        # This is just for testing.
        # TODO Remove this 'IF' after creating a testing database and a testing instance (probably in cloud).
        if Medic.objects.count() == 0:
            Medic.objects.create(username='juan', password='1234', name='juan',
                                 last_name='gomez', license='matricula #15433')
            Medic.objects.create(username='maria76', password='7070', name='maria',
                                 last_name='martinez vega', license='matricula #1342')
        medics = Medic.objects.all()
        serializer = MedicSerializer(medics, many=True, context={'request': request})
        return Response(serializer.data)
