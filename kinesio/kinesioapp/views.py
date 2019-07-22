from django.shortcuts import render
from django.views import generic
from users.models import SecretQuestion
from django.http import HttpResponse


class IndexView(generic.View):

    def get(self, request):
        return render(request, 'kinesioapp/index.html')


class SecretQuestionView(generic.View):
    def get(self, request):

        questions = SecretQuestion.objects.all()

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})

    def post(self, request):
        response = HttpResponse("Devolvi basura")

        response.status_code = 400
        return response
