# healthhub_backend/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    Medecin,
    Infermier,
    Laboratin,
    Radiologue,
    CentreHospitalier,
    Patient,
    DossierMedical,
    Consultation,
    Ordonnance,
    Medicament,
    OrdonnanceMedicament,
    ActiviteInfermier,
    # NurseMedication,
    ResultatLabo,
    HealthMetrics,
    Examen,
    ResultatRadio,
)

from rest_framework_api_key.models import APIKey




@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'centreHospitalier')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'centreHospitalier')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

# Register Profile Models
admin.site.register(Medecin)
admin.site.register(Infermier)
admin.site.register(Laboratin)
admin.site.register(Radiologue)

# Register Other Models
admin.site.register(CentreHospitalier)
admin.site.register(Patient)
admin.site.register(DossierMedical)
admin.site.register(Consultation)
admin.site.register(Ordonnance)
admin.site.register(Medicament)
admin.site.register(OrdonnanceMedicament)
admin.site.register(ActiviteInfermier)
# admin.site.register(NurseMedication)
admin.site.register(ResultatLabo)
admin.site.register(HealthMetrics)
admin.site.register(Examen)
admin.site.register(ResultatRadio)
