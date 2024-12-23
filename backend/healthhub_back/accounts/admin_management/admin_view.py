# accounts/admin_management/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from .admin_serializers import AdminUserCreateSerializer, AdminUserSerializer
from .admin_service import create_user_account, list_all_users, get_user_by_id
from rest_framework.exceptions import ValidationError

# Custom permission to allow only admin users
class IsAdminUserCustom(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAdminUserCustom]

    def post(self, request, *args, **kwargs):
        user = create_user_account(request.data)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data, status=201)

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserCustom]

    def get_queryset(self):
        return list_all_users()

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserCustom]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_user_by_id(user_id)