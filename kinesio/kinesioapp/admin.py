from django.contrib import admin

# Register your models here.
from .models import Medic, Patient, ClinicalHistory, ClinicalSession


class MedicAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'name', 'last_name']


class PatientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'name', 'last_name']

class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description', 'status']

class ClinicalSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'status']


admin.site.register(Medic, MedicAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(ClinicalHistory, ClinicalHistoryAdmin)
admin.site.register(ClinicalSession, ClinicalSessionAdmin)
