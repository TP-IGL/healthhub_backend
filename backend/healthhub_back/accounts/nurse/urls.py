from django.urls import path
from .nurse_view import (
    NurseActiviteListView,
    StartActiviteView,
    ValidateActiviteView,
    HistoriqueActivitesView,
)

urlpatterns = [
    path('activites/', NurseActiviteListView.as_view(), name='nurse_activites_list'), # Nurse can see the activities that are planned
    path('activites/<uuid:activiteinfermier_id>/start/', StartActiviteView.as_view(), name='start_activity'), # Nurse starts a activity which gonna update the status of the activity from planifie to en cours
    path('activites/<uuid:activiteinfermier_id>/validate/', ValidateActiviteView.as_view(), name='validate_activity'), # Nurse validates a activity which gonna update the status of the activity from en cours to termine and also save the results to the db
    path('activites/historique/', HistoriqueActivitesView.as_view(), name='activity_history'),  # Historique des activités
]