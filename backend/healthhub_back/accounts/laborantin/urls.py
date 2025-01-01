# urls.py

from django.urls import path
from .laborantin_views import ExamListView, SubmitLabTestView, LabResultHistoryView

urlpatterns = [
    path('exams/', ExamListView.as_view(), name='lab-exam-list'),
    path('submit-test/', SubmitLabTestView.as_view(), name='submit-lab-test'),
    path('patient-history/<str:patient_nss>/', LabResultHistoryView.as_view(), name='lab-result-history'),
]