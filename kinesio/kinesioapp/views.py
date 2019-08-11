from django.shortcuts import render
from django.views import generic
from users.models import SecretQuestion
from .models import ClinicalSession
from django.http import HttpResponse
from django.contrib.auth import logout


class IndexView(generic.View):

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.is_medic:

                return render(request, 'kinesioapp/index.html', {'patients': user.related_patients})
            else:
                sessions = ClinicalSession.objects.accessible_by(user=user)
                return render(request, 'kinesioapp/index.html', {'sessions': sessions})
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
        patient_id = request.GET.get("patient_id", None)
        sessions = ClinicalSession.objects.filter(patient_id=patient_id)
        return render(request, 'kinesioapp/users/clinical_history.html', {'sessions': sessions})


class ClinicalSessionView(generic.View):
    def get(self, request):

        clinical_session_id = request.GET.get("clinical_session_id", None)
        return render(request, 'kinesioapp/users/clinical_session.html')
