# common/auth/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import LoginSerializer, ChangePasswordSerializer
from .service import login_user, change_user_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model


# Handles user login and returns an authentication token.
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # Allow non-authenticated users to access

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = login_user(serializer.validated_data['username'], serializer.validated_data['password'])
        return Response({'token': token}, status=status.HTTP_200_OK)


# Allows authenticated users to change their password
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_user_password(
            request.user,
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password']
        )
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)