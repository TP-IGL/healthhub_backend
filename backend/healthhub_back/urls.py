from django.urls import include, path
from .views.hello_view import HelloList
# Routes 
urlpatterns = [
    path("hello/",HelloList.as_view(),name="hello-list"),
    path('admin/', include('healthhub_back.accounts.admin_management.urls')),
    path("auth/",include("healthhub_back.common.auth.urls")),
    path('medecin/', include('healthhub_back.accounts.doctor.urls')),  # Médecin functionalities
    path('infermier/', include('healthhub_back.accounts.nurse.urls')),  # Infermier functionalities
    path('radiologue/', include('healthhub_back.accounts.radiologue.urls')),  # Radiologue functionalities
]