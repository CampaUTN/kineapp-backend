from django.shortcuts import render
from django.views import generic
from users.models import SecretQuestion, Patient
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ClinicalSession, Image, Video, Exercise


class IndexView(generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
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
    def get(self, request: HttpRequest) -> HttpResponse:
        questions = SecretQuestion.objects.order_by('description')

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})


class NoUserView(generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'kinesioapp/login/no_user.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse("User logout")


class ClinicalHistoryView(LoginRequiredMixin, generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        patient_id = request.GET.get("patient_id", None)
        patient = Patient.objects.get(pk=patient_id)
        sessions = ClinicalSession.objects.filter(patient_id=patient_id).order_by('-id')
        return render(request, 'kinesioapp/users/clinical_history.html',
                      {'sessions': sessions, 'patient': patient.user})


class ClinicalSessionView(LoginRequiredMixin, generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        clinical_session_id = request.GET.get("clinical_session_id", None)
        clinical_session = ClinicalSession.objects.get(pk=clinical_session_id)
        return render(request, 'kinesioapp/users/clinical_session.html', {'clinical_session': clinical_session})


class TimelapseView(LoginRequiredMixin, generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        tag = request.GET.get("tag", None)
        patient_id = request.GET.get("patient_id", None)
        images = Image.objects.filter(clinical_session__patient_id=patient_id, tag=tag)

        return render(request, 'kinesioapp/users/timelapse.html', {'images': images})


class PublicVideosView(LoginRequiredMixin, generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        videos = Video.objects.filter(owner=user)
        return render(request, 'kinesioapp/users/public_video.html', {'videos': videos})


class RoutineView(LoginRequiredMixin, generic.View):
    def get(self, request: HttpRequest) -> HttpResponse:
        patient_id = request.GET.get("patient_id", None)
        exercises = Exercise.objects.filter(patient_id=patient_id)
        active_days = [exercise.day for exercise in Exercise.objects.filter(patient_id=patient_id).distinct('day')]
        return render(request, 'kinesioapp/users/routine.html', {'exercises': exercises, 'days_range': range(7), 'active_days': active_days})
