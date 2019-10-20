from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .models import SecretQuestion


class SecretQuestionView(generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        questions = SecretQuestion.objects.order_by('description')

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})


class NoUserView(generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'kinesioapp/login/no_user.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse("User logout")
