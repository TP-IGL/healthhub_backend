from django.urls import path
from .doctor_view import (
    SearchAndRetrieveDossierView,
    CreateConsultationView,
    ConsultationListView,
    ConsultationDetailView,
    ConsultationSummaryView,
)

urlpatterns = [
    # Patient Search and Dossier Retrieval
    path('dossier/', SearchAndRetrieveDossierView.as_view(), name='search_and_retrieve_dossier'),

    # Consultation Management
    path('consultations/', ConsultationListView.as_view(), name='consultation_list'),
    path('consultations/create/', CreateConsultationView.as_view(), name='create_consultation'),
    path('consultations/<uuid:consultation_id>/', ConsultationDetailView.as_view(), name='consultation_detail'),
    path('consultations/<uuid:consultation_id>/summary/', ConsultationSummaryView.as_view(), name='consultation_summary'),
]