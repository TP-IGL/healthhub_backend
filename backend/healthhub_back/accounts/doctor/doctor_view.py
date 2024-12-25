from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .doctor_serializers import (
    ConsultationCreateSerializer,
    ConsultationSerializer,
    ConsultationSummarySerializer,
    PatientSerializer,
    DossierMedicalSerializer
)
from rest_framework.permissions import IsAuthenticated
from .doctor_service import (
    search_patient,
    visualize_medical_record,
    create_consultation
)
from healthhub_back.models import Consultation, Medecin, Patient
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class IsMedecin(permissions.BasePermission):
    """
    Allows access only to users with role 'medecin'.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'medecin' or request.user.role == 'admin' ) 
        )

class DoctorPatientsView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Check if the user is a doctor
        try:
            doctor = Medecin.objects.get(user=self.request.user)
            # Return all patients associated with this doctor
            return Patient.objects.filter(medecin=doctor)
        except Medecin.DoesNotExist:
            return Patient.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(
                    {"message": "No patients found for this doctor"},
                    status=status.HTTP_200_OK
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class SearchAndRetrieveDossierView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMedecin]
    serializer_class = DossierMedicalSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query to find patient's medical record",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: DossierMedicalSerializer,
            400: 'Bad Request - Query parameter is missing',
            403: 'Forbidden - No permission to access this patient\'s dossier',
            404: 'Not Found - Patient not found'
        }
    )

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        if not query:
            return Response(
                {'error': 'Query parameter is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            patient = search_patient(query)
            # Ensure the patient is assigned to the authenticated médecin
            if patient.medecin.user != request.user:
                return Response(
                    {'error': 'You do not have permission to access this patient\'s dossier.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            dossier = visualize_medical_record(patient)
            serializer = self.get_serializer(dossier)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CreateConsultationView(generics.CreateAPIView):
    """
    Allows the médecin to create a new consultation, including ordonnances or complementary exams.
    """
    permission_classes = [permissions.IsAuthenticated, IsMedecin]
    serializer_class = ConsultationCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            consultation = serializer.save()
            response_serializer = ConsultationSerializer(consultation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConsultationListView(generics.ListAPIView):
    """
    Allows the médecin to list all their consultations.
    """
    permission_classes = [permissions.IsAuthenticated, IsMedecin]
    serializer_class = ConsultationSerializer

    def get_queryset(self):
        medecin = self.request.user.medecin
        return Consultation.objects.filter(dossier__patient__medecin=medecin)


class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific consultation.
    """
    permission_classes = [permissions.IsAuthenticated, IsMedecin]
    serializer_class = ConsultationSerializer
    lookup_field = 'consultation_id'

    def get_queryset(self):
        medecin = self.request.user.medecin
        return Consultation.objects.filter(dossier__patient__medecin=medecin)

    def get_object(self):
        consultation = get_object_or_404(Consultation, consultationID=self.kwargs['consultation_id'], dossier__patient__medecin=self.request.user.medecin)
        return consultation

    def delete(self, request, *args, **kwargs):
        consultation = self.get_object()
        consultation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConsultationSummaryView(generics.RetrieveAPIView):
    """
    Retrieves a detailed summary of a specific consultation, including patient history.
    """
    permission_classes = [permissions.IsAuthenticated, IsMedecin]
    serializer_class = ConsultationSummarySerializer
    lookup_field = 'consultation_id'

    def get_queryset(self):
        medecin = self.request.user.medecin
        return Consultation.objects.filter(dossier__patient__medecin=medecin)

    def get_object(self):
        consultation = get_object_or_404(Consultation, consultationID=self.kwargs['consultation_id'], dossier__patient__medecin=self.request.user.medecin)
        return consultation