# common/auth/services.py

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ValidationError


# Authenticates user credentials and returns a token.
def login_user(username, password):
    user = authenticate(username=username, password=password)
    if not user:
        raise AuthenticationFailed('Invalid username or password.')
    token, created = Token.objects.get_or_create(user=user)
    return token.key

def change_user_password(user, old_password, new_password):
    if not user.check_password(old_password):
        raise ValidationError('Old password is incorrect.')
    user.set_password(new_password)
    user.save()
    # Optionally, delete the old token to force re-login
    Token.objects.filter(user=user).delete()