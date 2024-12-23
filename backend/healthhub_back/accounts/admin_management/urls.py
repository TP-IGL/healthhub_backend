# accounts/admin_management/urls.py

from django.urls import path
from .admin_view import AdminUserCreateView, AdminUserListView, AdminUserDetailView

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/create/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('users/<uuid:user_id>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]