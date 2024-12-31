# urls.py
from django.urls import path
from .laborantin_views import (
    LaborantinExaminationListView,
    LaborantinExaminationDetailView,
    ResultatLaboCreateView,
    ResultatLaboUpdateView,
    HealthMetricCreateView,
    LaborantinStatisticsView,
    PatientLabHistoryView
)

urlpatterns = [
    path(
        'laborantin/examinations/',
        LaborantinExaminationListView.as_view(),
        name='laborantin-examination-list'
    ),
    path(
        'laborantin/examinations/<uuid:examenID>/',
        LaborantinExaminationDetailView.as_view(),
        name='laborantin-examination-detail'
    ),
    path(
        'laborantin/examinations/<uuid:examenID>/results/',
        ResultatLaboCreateView.as_view(),
        name='laborantin-result-create'
    ),
    path(
        'laborantin/results/<uuid:resLaboID>/',
        ResultatLaboUpdateView.as_view(),
        name='laborantin-result-update'
    ),
    path(
        'laborantin/results/<uuid:resLaboID>/metrics/',
        HealthMetricCreateView.as_view(),
        name='laborantin-metric-create'
    ),
    path(
        'laborantin/statistics/',
        LaborantinStatisticsView.as_view(),
        name='laborantin-statistics'
    ),
    path(
        'laborantin/patients/<uuid:patient_id>/lab-history/',
        PatientLabHistoryView.as_view(),
        name='patient-lab-history'
    )
]