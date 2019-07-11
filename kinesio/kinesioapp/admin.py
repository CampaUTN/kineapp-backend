from django.contrib import admin
from .models import ClinicalHistory, ClinicalSession


class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description', 'status']


class ClinicalSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'status']


admin.site.register(ClinicalHistory, ClinicalHistoryAdmin)
admin.site.register(ClinicalSession, ClinicalSessionAdmin)
