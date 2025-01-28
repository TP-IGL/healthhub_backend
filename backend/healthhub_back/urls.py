from django.urls import include, path
# Routes 
urlpatterns = [
    path('admin/', include('healthhub_back.accounts.admin_management.urls')),
    path("auth/",include("healthhub_back.common.auth.urls")),
    path('medecin/', include('healthhub_back.accounts.doctor.urls')),  # Médecin functionalities
    path('infermier/', include('healthhub_back.accounts.nurse.urls')),  # Infermier functionalities
    path('radiologue/', include('healthhub_back.accounts.radiologue.urls')),  # Radiologue functionalities
    path('patient/', include('healthhub_back.accounts.patient.urls')),  # Patient functionalities
    path('laborantin/', include('healthhub_back.accounts.laborantin.urls')),  # Laborantin functionalities
    path('sgph/', include('healthhub_back.accounts.sgph.urls')),  # Add this line
]