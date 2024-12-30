# urls.py

from django.urls import path
from .patient_view import PatientMedicalFileView

urlpatterns = [
    path('/medical-file/<uuid:patient_id>/', 
         PatientMedicalFileView.as_view(), 
         name='patient-medical-file'),
]