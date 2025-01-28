# sgbh/urls.py

from django.urls import path
from . import sgph_view as views

urlpatterns = [
    path('ordonnances/', views.get_ordonnances, name='get_ordonnances'),
    path('ordonnances/<uuid:ordonnance_id>/', views.get_ordonnance, name='get_ordonnance'),
    path('ordonnances/<uuid:ordonnance_id>/validate/', views.validate_ordonnance, name='validate_ordonnance'),
]