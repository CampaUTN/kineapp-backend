from django.contrib import admin
from .models import ClinicalSession


class ClinicalSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'status']


admin.site.register(ClinicalSession, ClinicalSessionAdmin)
