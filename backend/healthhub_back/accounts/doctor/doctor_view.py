from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status

from healthhub_back.models import Patient, DossierMedical, User
from healthhub_back.accounts.patient.patient_serializers import PatientsSerializer, DossierMedicalDetailSerializer
from rest_framework import permissions

class IsMedecin(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role == 'medecin' or request.user.role == 'admin'  
    
class DoctorPatientListView(generics.ListAPIView):
    """
    View for listing all patients associated with a doctor
    """
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = PatientsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'prenom', 'NSS']
    ordering_fields = ['nom', 'prenom', 'dateNaissance', 'createdAt']
    ordering = ['nom']  # default ordering

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')


        print(self.request.user.id)
        print(doctor_id)
        # Verify the requesting user is the doctor or an admin
        if str(self.request.user.id) != str(doctor_id) :
            raise PermissionDenied("You can only view your own patients")

        return Patient.objects.filter(
            medecin__user__id=doctor_id,
        ).select_related(
            'medecin',
            'medecin__user',
            'centreHospitalier'
        )

class PatientSearchView(generics.RetrieveAPIView):
    """
    View for searching patient by NSS or QR code and returning complete medical file
    """
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = DossierMedicalDetailSerializer

    def get_queryset(self):
        return DossierMedical.objects.select_related(
            'patient',
            'patient__medecin',
            'patient__medecin__user',
            'patient__centreHospitalier'
        ).prefetch_related(
            'consultation_set',
            'consultation_set__ordonnance_set',
            'consultation_set__ordonnance_set__ordonnancemedicament_set',
            'consultation_set__ordonnance_set__ordonnancemedicament_set__med',
            'consultation_set__examen_set',
            'consultation_set__examen_set__resultatlabo_set',
            'consultation_set__examen_set__resultatlabo_set__health_metrics',
            'consultation_set__examen_set__resultatradio_set',
            'consultation_set__activiteinfermier_set',
            'consultation_set__activiteinfermier_set__infermier'
        )

    def get(self, request,*args, **kwargs):
        # First, find the patient based on search criteria
        search_type = kwargs.get('search_type')
        search_value = kwargs.get('search_value')
        try:
            if search_type == 'nss':
                patient = get_object_or_404(Patient, 
                    NSS=search_value,
                )
            elif search_type == 'qr':
                dossier = get_object_or_404(DossierMedical, 
                    qrCode=search_value,
                )
                patient = dossier.patient
            else:
                return Response(
                    {"error": "Invalid search type"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check permissions
            if not self.has_permission_to_access(request.user, patient):
                return Response(
                    {"error": "You don't have permission to access this medical file"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get the complete medical file
            dossier = get_object_or_404(
                self.get_queryset(),
                patient=patient
            )

            serializer = self.serializer_class(dossier)
            return Response(serializer.data)

        except (Patient.DoesNotExist, DossierMedical.DoesNotExist):
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def has_permission_to_access(self, user, patient):
        # If user is the patient's assigned doctor
        if patient.medecin.user == user:
            return True

        # If user is a doctor from the same hospital
        if (user.role == 'medecin' and 
            user.centreHospitalier == patient.centreHospitalier):
            return True
        
        if (user.role == 'admin'):
            return True

        return False