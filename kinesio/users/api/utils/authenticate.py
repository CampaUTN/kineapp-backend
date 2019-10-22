from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
from django.shortcuts import get_object_or_404
from rest_framework.request import HttpRequest

from ...models import User, SecretQuestion


def authenticate(request: HttpRequest, user: User, secret_question_id: int, answer: str) -> Response:
    """ This function is not a view by itself.
        It's just a way to reuse logic between 'login' and 'continue_session' endpoints. """
    # Check secret question existence
    get_object_or_404(SecretQuestion, id=secret_question_id)

    # Check user status (active / banned)
    if not user.is_active:
        return Response({'message': 'Your account has been blocked due to many access errors'},
                        status=status.HTTP_401_UNAUTHORIZED)

    # Check whether the question and the answer are correct
    if user.check_question_and_answer(secret_question_id, answer):
        auth.authenticate(username=user.username, password=answer)
        auth.login(request, user)
        return Response({'message': 'Logged in', 'token': user.get_or_create_token().key},
                        status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid question or answer (no more details are given due to security reasons).'},
                        status=status.HTTP_401_UNAUTHORIZED)
