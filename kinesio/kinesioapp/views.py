from django.shortcuts import render
from django.views import generic
from .models import Patient


class IndexView(generic.View):
    def get(self, request):
        return render(request, 'kinesioapp/index.html', {'posts': Patient.objects.all()})
