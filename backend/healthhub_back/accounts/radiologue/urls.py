from django.urls import path
from .radiologue_view import (
    RadiologueExamenListView,
    ExamenDetailView,
    StartExamenView,
    CreateResultatRadioView,
    ValidateExamenView,
    HistoriqueExamenView,
)

urlpatterns = [
    path('examens/', RadiologueExamenListView.as_view(), name='examens_list'), 
    path('examens/<uuid:examen_id>/', ExamenDetailView.as_view(), name='examens_detail'),  
    path('examens/<uuid:examen_id>/start/', StartExamenView.as_view(), name='start_examens'), 
    path('examens/<uuid:examen_id>/create-resultat-radio/', CreateResultatRadioView.as_view(), name='create_resultat_radio'),
    path('examens/<uuid:examen_id>/validate/', ValidateExamenView.as_view(), name='validate_examensy'), 
    path('examens/historique/', HistoriqueExamenView.as_view(), name='examens_history'),  
]
