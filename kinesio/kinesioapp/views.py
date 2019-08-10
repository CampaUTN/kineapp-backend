from django.shortcuts import render
from django.views import generic
from .models import ClinicalHistory
from users.models import SecretQuestion, UserQuerySet
from django.http import HttpResponse
from django.contrib.auth import logout


class IndexView(generic.View):

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.is_medic:

                return render(request, 'kinesioapp/index.html', {'patients': user.related_patients})
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
        clinical_history_id = request.GET.get("clinical_history_id", None)
        try:
            if clinical_history_id is None:
                patient_id = request.GET.get("patient_id", None)
                clinical_history = ClinicalHistory.objects.get(patient_id=patient_id, medic_id=request.user.pk)
            else:
                clinical_history = ClinicalHistory.objects.get(pk=clinical_history_id)

        except ClinicalHistory.DoesNotExist:
            return render(request, 'kinesioapp/users/clinical_history.html')

        return render(request, 'kinesioapp/users/clinical_history.html', {'clinical_history': clinical_history})


class ClinicalSessionView(generic.View):
    def get(self, request):

        clinical_session_id = request.GET.get("clinical_session_id", None)
        return render(request, 'kinesioapp/users/clinical_session.html')
