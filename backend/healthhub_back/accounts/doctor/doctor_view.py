from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from healthhub_back.models import Patient, DossierMedical , Consultation , DossierMedical,Consultation,Examen,Radiologue,Laboratin ,    Ordonnance, Consultation, OrdonnanceMedicament, Medicament
from healthhub_back.accounts.patient.patient_serializers import PatientsSerializer, DossierMedicalDetailSerializer, ConsultationsSerializer,ExamensSerializer,OrdonnancesSerializer, MedicamentsSerializer
from rest_framework import permissions
from .doctor_serializers import (
    ConsultationCreateUpdateSerializer,
    ExaminationCreateSerializer, 
    RadiologueListSerializer,
    LaborantinListSerializer,
    OrdonnanceCreateSerializer,
    OrdonnanceUpdateSerializer,
    MedicamentCreateSerializer,
    PrescriptionCreateSerializer,
)


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
            'consultation_set__examen_set__resultatlabo_set__healthmetrics_set',  # Updated here
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
    
# consultations

# create consultation
class ConsultationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = ConsultationCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save()

# get & update consultation
class ConsultationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    queryset = Consultation.objects.select_related(
        'dossier__patient__medecin',
        'dossier__patient__medecin__user',
        'dossier__patient__centreHospitalier'
    ).prefetch_related(
        'ordonnance_set',
        'ordonnance_set__ordonnancemedicament_set',
        'ordonnance_set__ordonnancemedicament_set__med',
        'examen_set',
        'examen_set__resultatlabo_set',
        'examen_set__resultatlabo_set__healthmetrics_set',
        'examen_set__resultatradio_set',
        'activiteinfermier_set',
        'activiteinfermier_set__infermier'
    )
    lookup_field = 'consultationID'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ConsultationCreateUpdateSerializer
        return ConsultationsSerializer

    def has_permission_to_access(self, consultation):
        user = self.request.user
        return True
        """ return (user.centreHospitalier == 
                consultation.dossier.patient.centreHospitalier) """

    def get_object(self):
        obj = super().get_object()
        if not self.has_permission_to_access(obj):
            raise PermissionDenied(
                "You don't have permission to access this consultation"
            )
        return obj
    
########################### Examination ############################################



class ExaminationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = ExaminationCreateSerializer

    def get_consultation(self):
        return get_object_or_404(
            Consultation, 
            consultationID=self.kwargs['consultation_id']
        )

    def perform_create(self, serializer):
        consultation = self.get_consultation()
        print('H  ',consultation.dossier.patient.centreHospitalier)
        print(self.request.user)
        if consultation.dossier.patient.centreHospitalier != self.request.user.centreHospitalier:
            raise PermissionDenied("Not authorized for this hospital's patients")
        serializer.save(
            consultation=consultation,
            etat='planifie'
        )

class RadiologueListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = RadiologueListSerializer

    def get_queryset(self):
        hospital_id = self.kwargs['hospital_id']
        return Radiologue.objects.filter(
            user__centreHospitalier_id=hospital_id
        ).select_related('user')

class LaborantinListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = LaborantinListSerializer

    def get_queryset(self):
        hospital_id = self.kwargs['hospital_id']
        return Laboratin.objects.filter(
            user__centreHospitalier_id=hospital_id
        ).select_related('user')

class ExaminationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = ExamensSerializer
    lookup_field = 'examenID'

    def get_queryset(self):
        return Examen.objects.select_related(
            'consultation__dossier__patient__medecin__user',
            'consultation__dossier__patient__centreHospitalier'
        ).prefetch_related(
            'resultatlabo_set__healthmetrics_set',
            'resultatradio_set'
        )

    def get_object(self):
        obj = super().get_object()
        if obj.consultation.dossier.patient.centreHospitalier != self.request.user.centreHospitalier:
            raise PermissionDenied("Not authorized for this hospital's examinations")
        return obj
    
###########################      Prescription         ##############################


class MedicamentCreateView(generics.CreateAPIView):
    """Create a new medication"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = MedicamentCreateSerializer
    queryset = Medicament.objects.all()

class OrdonnanceCreateView(generics.CreateAPIView):
    """Create a new prescription for a consultation"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = OrdonnanceCreateSerializer

    def perform_create(self, serializer):
        consultation = get_object_or_404(
            Consultation, 
            consultationID=self.kwargs['consultation_id']
        )

        # Check if doctor is authorized
        if consultation.dossier.patient.medecin.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to create prescriptions for this patient"
            )

        serializer.save(consultation=consultation)

class OrdonnanceDetailView(generics.RetrieveAPIView):
    """Get prescription details"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = OrdonnancesSerializer
    lookup_field = 'ordonnanceID'
    queryset = Ordonnance.objects.all()

    def get_queryset(self):
        return Ordonnance.objects.select_related(
            'consultation__dossier__patient__medecin__user'
        ).prefetch_related(
            'ordonnancemedicament_set__med'
        )

    def get_object(self):
        obj = super().get_object()
        if obj.consultation.dossier.patient.medecin.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to view this prescription"
            )
        return obj

class ConsultationOrdonnanceListView(generics.ListAPIView):
    """List all prescriptions for a consultation"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = OrdonnancesSerializer

    def get_queryset(self):
        consultation = get_object_or_404(
            Consultation, 
            consultationID=self.kwargs['consultation_id']
        )

        # Check if doctor is authorized
        if consultation.dossier.patient.medecin.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to view prescriptions for this patient"
            )

        return Ordonnance.objects.filter(
            consultation=consultation
        ).select_related(
            'consultation'
        ).prefetch_related(
            'ordonnancemedicament_set__med'
        )

class OrdonnanceUpdateView(generics.UpdateAPIView):
    """Update prescription validation status"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = OrdonnanceUpdateSerializer
    lookup_field = 'ordonnanceID'
    queryset = Ordonnance.objects.all()
    http_method_names = ['patch']

    def get_object(self):
        obj = super().get_object()
        if obj.consultation.dossier.patient.medecin.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to update this prescription"
            )
        return obj

class MedicamentListView(generics.ListAPIView):
    """List all available medications"""
    permission_classes = [IsAuthenticated, IsMedecin]
    serializer_class = MedicamentsSerializer
    queryset = Medicament.objects.all()

    def get_queryset(self):
        queryset = Medicament.objects.all()

        # Filter by type if provided
        med_type = self.request.query_params.get('type', None)
        if med_type:
            queryset = queryset.filter(type=med_type)

        # Search by name if provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(nom__icontains=search)

        return queryset
    


class PrescriptionCreateView(generics.CreateAPIView):
    serializer_class = PrescriptionCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_consultation(self, consultation_id):
        try:
            return Consultation.objects.get(pk=consultation_id)
        except Consultation.DoesNotExist:
            return None

    def post(self, request, consultation_id, *args, **kwargs):
        consultation = self.get_consultation(consultation_id)
        if not consultation:
            return Response(
                {"detail": "Consultation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data, context={'consultation': consultation})
        serializer.is_valid(raise_exception=True)
        ordonnance = serializer.save()

        # Optionally, serialize the created Ordonnance to return in the response
        ordonnance_serializer = OrdonnancesSerializer(ordonnance)
        return Response(
            ordonnance_serializer.data,
            status=status.HTTP_201_CREATED
        )