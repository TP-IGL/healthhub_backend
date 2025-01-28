# sgbh/views.py

from django.shortcuts import get_object_or_404
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from healthhub_back.models import Ordonnance
from ..patient.patient_serializers import OrdonnancesSerializer

@api_view(["GET"])
@permission_classes([HasAPIKey])
def get_ordonnances(request):
    """
    Allow SGPH service to retrieve non-validated ordonnances
    """
    # get all ordonnance
    ordonnances = Ordonnance.objects.filter(valide=False)
    serializer = OrdonnancesSerializer(ordonnances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([HasAPIKey])
def get_ordonnance(request, ordonnance_id):
    """
    Allow SGPH service to retrieve an ordonnance by ID
    """
    ordonnance = get_object_or_404(Ordonnance, ordonnanceID=ordonnance_id)
    serializer = OrdonnancesSerializer(instance=ordonnance)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([HasAPIKey])
def validate_ordonnance(request, ordonnance_id):
    """
    Allow SGPH service to validate an ordonnance by ID
    """
    ordonnance = get_object_or_404(Ordonnance, ordonnanceID=ordonnance_id)
    ordonnance.valide = True
    ordonnance.save()

    serializer = OrdonnancesSerializer(instance=ordonnance)
    return Response(serializer.data, status=status.HTTP_200_OK)