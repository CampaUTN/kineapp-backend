from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from users.models import SecretQuestion, Patient
from .models import ClinicalSession, Image, Video, Exercise
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
        questions = SecretQuestion.objects.order_by('description')

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})


class NoUserView(generic.View):

    def get(self, request):
        return render(request, 'kinesioapp/login/no_user.html')


def logout_view(request):
    logout(request)
    return HttpResponse("User logout")


@method_decorator(login_required, name='dispatch')
class ClinicalHistoryView(generic.View):
    def get(self, request):
        patient_id = request.GET.get("patient_id", None)
        patient = Patient.objects.get(pk=patient_id)
        sessions = ClinicalSession.objects.filter(patient_id=patient_id).order_by('-id')
        return render(request, 'kinesioapp/users/clinical_history.html',
                      {'sessions': sessions, 'patient': patient.user})


@method_decorator(login_required, name='dispatch')
class ClinicalSessionView(generic.View):
    def get(self, request):
        clinical_session_id = request.GET.get("clinical_session_id", None)
        clinical_session = ClinicalSession.objects.get(pk=clinical_session_id)
        return render(request, 'kinesioapp/users/clinical_session.html', {'clinical_session': clinical_session})


@method_decorator(login_required, name='dispatch')
class TimelapseView(generic.View):
    def get(self, request):
        tag = request.GET.get("tag", None)
        patient_id = request.GET.get("patient_id", None)
        images = Image.objects.filter(clinical_session__patient_id=patient_id, tag=tag)

        return render(request, 'kinesioapp/users/timelapse.html', {'images': images})


@method_decorator(login_required, name='dispatch')
class PublicVideosView(generic.View):
    def get(self, request):
        user = request.user
        videos = Video.objects.filter(owner=user)
        return render(request, 'kinesioapp/users/public_video.html', {'videos': videos})


@method_decorator(login_required, name='dispatch')
class RoutineView(generic.View):
    def get(self, request):
        patient_id = request.GET.get("patient_id", None)
        exercises = Exercise.objects.filter(patient_id=patient_id)
        days = Exercise.objects.filter(patient_id=patient_id).values('day').distinct() #fixme needed for complete days that no have exercises. Looking for another solution
        active_days = []
        for day in days:
            active_days.append(day['day'])
        return render(request, 'kinesioapp/users/routine.html', {'exercises': exercises, 'days_range': range(7), 'active_days': active_days})
