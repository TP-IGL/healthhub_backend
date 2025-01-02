# common/auth/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import LoginSerializer, ChangePasswordSerializer
from .service import login_user, change_user_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# Handles user login and returns an authentication token.
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import LoginSerializer
from .service import login_user
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Authenticate user and generate token
        token = login_user(serializer.validated_data['username'], serializer.validated_data['password'])

        # Retrieve user information
        user = User.objects.get(username=serializer.validated_data['username'])

        # Prepare response data
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'centre_hospitalier_id': user.centreHospitalier.id if user.centreHospitalier else None
        }

        # Return token along with user data
        return Response({'token': token, 'user': user_data}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Handles user logout by deleting the authentication token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token to log them out
            request.user.auth_token.delete()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({'detail': 'Token not found.'}, status=status.HTTP_400_BAD_REQUEST)

    # Optionally, handle GET requests if Swagger uses GET for logout
    def get(self, request):
        return self.post(request)

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