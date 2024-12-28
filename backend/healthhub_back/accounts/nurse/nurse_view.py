from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from healthhub_back.models import Consultation, ActiviteInfermier
from .nurse_serializers import  ValidateActiviteSerializer, NurseConsultationDetailSerializer
from rest_framework.views import APIView

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from django.db.models import Q



class IsInfermier(permissions.BasePermission):
    """
    Allows access only to users with role 'infermier'.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'infermier' or request.user.role == 'Infermier' or request.user.role == 'admin' ) 
        )
    

class ActiviteFilter(filters.FilterSet):
    # Add filters for activity type and status
    status = filters.ChoiceFilter(choices=ActiviteInfermier.STATUS_CHOICES)
    type_activite = filters.ChoiceFilter(choices=ActiviteInfermier.TYPE_ACTIVITE_CHOICES)

    class Meta:
        model = ActiviteInfermier
        fields = ['status', 'type_activite']


class NurseActiviteListView(generics.ListAPIView):
    """
    Allows the nurse to view all activities they are associated with, including activity and patient details,
    with filtering, searching, and pagination.
    """
    permission_classes = [permissions.IsAuthenticated, IsInfermier]
    serializer_class = NurseConsultationDetailSerializer

    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = ActiviteFilter

    def get_queryset(self):
        """
        Filter activities based on parameters like status, type of activity, and search query.
        """
        # Get nurse's activities that are associated with this nurse
        infermier = self.request.user.infermier
        queryset = ActiviteInfermier.objects.filter(
            infermier=infermier,
        ).select_related(
            'consultation__dossier__patient'
        ).distinct()

        # Apply filters from the request if they exist
        if self.request.GET.get('status'):
            status_filter = self.request.GET.get('status')
            queryset = queryset.filter(status=status_filter)

        if self.request.GET.get('type_activite'):
            type_activite = self.request.GET.get('type_activite')
            queryset = queryset.filter(typeActivite=type_activite)

        if self.request.GET.get('search'):
            search_query = self.request.GET.get('search')
            queryset = queryset.filter(
                Q(consultation__dossier__patient__nom__icontains=search_query) |
                Q(consultation__dossier__patient__prenom__icontains=search_query) |
                Q(consultation__dossier__patient__NSS__icontains=search_query)
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        # Apply filtering, searching, and ordering
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"message": "No activities found for this nurse using the search filters."},
                status=status.HTTP_200_OK
            )

        # Serialize data
        data = []
        for activity in queryset:
            # Get related consultation and patient details
            consultation = activity.consultation
            patient = consultation.dossier.patient

            serialized_data = NurseConsultationDetailSerializer({
                "patient": patient,
                "activities": [activity],  # Here we include the current activity
                "consultation": consultation,
            }).data

            data.append(serialized_data)

        return Response(data, status=status.HTTP_200_OK)


class StartActiviteView(APIView):
    """
    Allows the nurse to start an activity by updating its status to 'en cours'.
    """
    permission_classes = [permissions.IsAuthenticated, IsInfermier]

    def patch(self, request, *args, **kwargs):
        activiteinfermier_id = kwargs.get("activiteinfermier_id")
        activiteinfermier = get_object_or_404(ActiviteInfermier, id=activiteinfermier_id)

        # Update the status
        activiteinfermier.status = "en_cours"
        activiteinfermier.save()

        return Response(
            {"message": f"Activity '{activiteinfermier.id}' updated to 'en_cours'."},
            status=status.HTTP_200_OK,
        )
        
        
class ValidateActiviteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInfermier]
    serializer_class = ValidateActiviteSerializer


    def patch(self, request, *args, **kwargs):
        # Validate the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nurse_observations = serializer.validated_data.get('nurse_observations')

        # Get the consultation object or return a 404
        activiteinfermier_id = kwargs.get('activiteinfermier_id')
        activiteinfermier = get_object_or_404(ActiviteInfermier, id=activiteinfermier_id)

        if not activiteinfermier:
            return Response(
                {"message": "Activity not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        activiteinfermier.status = "termine"
        activiteinfermier.nurse_observations = nurse_observations
        activiteinfermier.save()

        return Response(
            {"message": f"Activity '{activiteinfermier.id}' validated."},
            status=status.HTTP_200_OK
        )
    

class HistoriqueActivitesView(generics.ListAPIView):
    """
    Allows the nurse to view all activities they have completed.
    """
    permission_classes = [permissions.IsAuthenticated, IsInfermier]
    serializer_class = ValidateActiviteSerializer

    def get_queryset(self):
        # Get nurse's activities
        infermier = self.request.user.infermier
        return ActiviteInfermier.objects.filter(
            infermier=infermier,
            status="termine"
        ).select_related(
            'consultation__dossier__patient'
        ).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"message": "No activities done found for this nurse."},
                status=status.HTTP_200_OK
            )

        # Prepare data for serialization
        data = []
        
    
        for activity in queryset:
            # Get related consultation and patient details
                consultation = activity.consultation
                patient = consultation.dossier.patient

                serialized_data = NurseConsultationDetailSerializer({
                    "patient": patient,
                    "activities": [activity],  # Here we include the current activity
                    "consultation": consultation,
                }).data

                data.append(serialized_data)

        return Response(data, status=status.HTTP_200_OK)
    


class ActiviteDetailView(generics.RetrieveAPIView):
    """
    Allows the nurse to view a specific activity.
    """
    permission_classes = [permissions.IsAuthenticated, IsInfermier]
    serializer_class = ValidateActiviteSerializer

    def get_queryset(self):
        # Get nurse's activities
        infermier = self.request.user.infermier
        return ActiviteInfermier.objects.filter(
            infermier=infermier
        )

    def get_object(self):
        activiteinfermier_id = self.kwargs.get('activiteinfermier_id')
        return get_object_or_404(self.get_queryset(), id=activiteinfermier_id)
    
    def get(self, request, *args, **kwargs):
        activity = self.get_object()
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)
