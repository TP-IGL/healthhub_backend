from django.urls import path
from .views import LoginView, ChangePasswordView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Added logout path
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]