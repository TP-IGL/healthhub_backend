from django.urls import path
from .doctor_view import (ActiviteInfermierCreateView, ConsultationCreateView, ConsultationDetailView, DoctorPatientListView, InfermierListView, PatientSearchView,
                          ExaminationCreateView, PrescriptionCreateView, RadiologueListView,LaborantinListView, ExaminationDetailView,OrdonnanceCreateView, OrdonnanceDetailView,
                        ConsultationOrdonnanceListView, OrdonnanceUpdateView,
                        MedicamentCreateView, MedicamentListView)

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
     # Examination
     path(
        'consultations/<uuid:consultation_id>/examinations/',
        ExaminationCreateView.as_view(),
        name='examination-create'
    ),
    # ActiviteInfermierCreateView
    ####
    path(
        'hospital/<int:hospital_id>/radiologues/',
        RadiologueListView.as_view(),
        name='radiologue-list'
    ),
    path(
        'hospital/<int:hospital_id>/laborantins/',
        LaborantinListView.as_view(),
        name='laborantin-list'
    ),
    # InfermierListView
    path(
        'hospital/<int:hospital_id>/infermiers/',
        InfermierListView.as_view(),
        name='laborantin-list'
    ),
    # now import ActiviteInfermierCreateView
    path(
        'infermier/',
        ActiviteInfermierCreateView.as_view(),
        name='examination-create'
    )
    ,
    path(
        'examinations/<uuid:examenID>/',
        ExaminationDetailView.as_view(),
        name='examination-detail'
    ),
    # prescription
    path(
        'prescriptions/<uuid:ordonnanceID>/',
        OrdonnanceDetailView.as_view(),
        name='prescription-detail'
    ),
    path(
        'consultations/<uuid:consultation_id>/prescriptions/list/',
        ConsultationOrdonnanceListView.as_view(),
        name='consultation-prescriptions'
    ),
    path(
        'prescriptions/<uuid:ordonnanceID>/update/',
        OrdonnanceUpdateView.as_view(),
        name='prescription-update'
    ),
    path(
        'consultations/<uuid:consultation_id>/prescriptions/',
        PrescriptionCreateView.as_view(),
        name='create-prescription'
    ),
]