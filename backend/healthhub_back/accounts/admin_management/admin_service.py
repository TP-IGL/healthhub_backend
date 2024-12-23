# accounts/admin_management/services.py

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .admin_serializers import AdminUserCreateSerializer, AdminUserSerializer

User = get_user_model()

def create_user_account(data):
    serializer = AdminUserCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return user

def list_all_users():
    return User.objects.all()

def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValidationError('User not found.')

def update_user(user, data):
    serializer = AdminUserSerializer(user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data

def delete_user(user):
    user.delete()