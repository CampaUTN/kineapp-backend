from django.shortcuts import render
from django.views import generic
from .models import ClinicalHistory
from users.models import SecretQuestion
from django.http import HttpResponse
from django.contrib.auth import logout


class IndexView(generic.View):

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'license'):
                patients = user.patients
                return render(request, 'kinesioapp/index.html', {'patients': patients})
            else:
                clinical_histories = ClinicalHistory.objects.filter(patient=user)
                return render(request, 'kinesioapp/index.html', {'clinical_histories': clinical_histories})
        else:
            return render(request, 'kinesioapp/index.html')


class SecretQuestionView(generic.View):
    def get(self, request):
        questions = SecretQuestion.objects.all()

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})


class NoUserView(generic.View):

    def get(self, request):
        return render(request, 'kinesioapp/login/no_user.html')


def logout_view(request):
    logout(request)
    return HttpResponse("User logout")


class ClinicalHistoryView(generic.View):
    def get(self, request):
        id_clinical_history = request.GET["id_clinical_history"]
        clinical_history = ClinicalHistory.objects.get(pk=id_clinical_history)
        if clinical_history is None:
            return render(request, 'kinesioapp/users/clinical_history.html')
        else:
            return render(request, 'kinesioapp/users/clinical_history.html', {'clinical_history': clinical_history})
