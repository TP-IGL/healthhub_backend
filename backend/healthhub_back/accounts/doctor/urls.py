from django.urls import path
from .doctor_view import ConsultationCreateView, ConsultationDetailView, DoctorPatientListView, PatientSearchView

urlpatterns = [
    # Doctor's patient list
    path('doctors/<str:doctor_id>/patients/', 
         DoctorPatientListView.as_view(), 
         name='doctor-patients'),

    path('medecin/patients/search/<str:search_type>/<str:search_value>/', 
          PatientSearchView.as_view(), 
          name='patient-search'),
          
     path('consultations/', 
         ConsultationCreateView.as_view(), 
         name='consultation-create'),
     
    path('consultations/<uuid:consultationID>/', 
         ConsultationDetailView.as_view(), 
         name='consultation-detail'),
]