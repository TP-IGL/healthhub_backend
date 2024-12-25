# accounts/admin_management/urls.py

from django.urls import path
from .admin_view import AdminUserCreateView, AdminUserListView, AdminUserDetailView, CentreHospitalierCreateView, CentreHospitalierListView, PatientCreateView

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/create/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('users/<uuid:user_id>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    # CentreHospitalier endpoints
    path('centre-hospitalier/create/', CentreHospitalierCreateView.as_view(), name='centre-hospitalier-create'),
    path('centre-hospitalier/', CentreHospitalierListView.as_view(), name='centre-hospitalier-list'),
    path('patients/create/', PatientCreateView.as_view(), name='patient-create'),
]