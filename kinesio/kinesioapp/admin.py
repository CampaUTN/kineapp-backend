from django.contrib import admin

# Register your models here.
from .models import Medic, Patient


class MedicAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'last_name']


class PatientAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'last_name']


admin.site.register(Medic, MedicAdmin)
admin.site.register(Patient, PatientAdmin)
