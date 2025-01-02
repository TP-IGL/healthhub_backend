# views.py
from django.db.models import F
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from healthhub_back.accounts.patient.patient_serializers import ExamensSerializer
from healthhub_back.models import Examen, ResultatLabo, Laboratin, Patient
from .laborantin_serializers import (
    ExamRequiredSerializer, ResultatLaboCreateSerializer, LabResultHistorySerializer, ResultatLaboHistorySerializer
)
from rest_framework.permissions import IsAuthenticated

# Custom permission to allow only lab technicians
class IsLaborantin(permissions.BasePermission):
    """
    Custom permission to allow only lab technicians.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'laborantin'

class ExamListView(generics.ListAPIView):
    """
    GET: Retrieve a list of all exams required by the lab technician.
    Each exam includes doctor_details and, if the exam is completed (etat='termine'),
    includes associated health metrics.
    """
    serializer_class = ExamRequiredSerializer
    permission_classes = [IsAuthenticated, IsLaborantin]

    def get_queryset(self):
        # Get the laborantin instance linked to the user
        try:
            laborantin = self.request.user.laboratin
        except Laboratin.DoesNotExist:
            return Examen.objects.none()

        # Filter exams of type 'labo' and associated with the hospital center
        laboratin = self.request.user.laboratin
        return Examen.objects.filter(
            type='labo',
            laborantin=laborantin,
            etat__in=['planifie', 'en_cours', 'termine']  # Include 'termine' to see results
        )

class SubmitLabTestView(generics.CreateAPIView):
    serializer_class = ResultatLaboCreateSerializer
    permission_classes = [IsAuthenticated, IsLaborantin]

    def create(self, request, *args, **kwargs):
        try:
            laboratin = request.user.laboratin
        except Laboratin.DoesNotExist:
            return Response({"detail": "Laborantin profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        if laboratin.nombreTests <= 0:
            return Response({"detail": "No remaining tests to perform."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'laboratin': laboratin})
        serializer.is_valid(raise_exception=True)

        examen = serializer.validated_data.get('examen')

        if not Examen.objects.filter(
            examenID=examen.examenID,
            type='labo',
            etat__in=['planifie', 'en_cours', 'termine'],
        ).exists():
            return Response({"detail": "Examen not found or not assigned to you."}, status=status.HTTP_400_BAD_REQUEST)

        examen.etat = 'en_cours'
        examen.save()

        resultat_labo = serializer.save()

        examen.etat = 'termine'
        examen.save()

        Laboratin.objects.filter(user_id=laboratin.user.id).update(nombreTests=F('nombreTests') - 1)

        return Response(ExamRequiredSerializer(examen).data, status=status.HTTP_201_CREATED)
    

class LabResultHistoryView(generics.ListAPIView):
    """
    GET: Retrieve history of lab results for a given patient by patient NSS.
    """
    serializer_class = ResultatLaboHistorySerializer
    permission_classes = [IsAuthenticated, IsLaborantin]

    def get_queryset(self):
        patient_nss = self.kwargs.get('patient_nss')

        # Optional: Validate if the patient exists
        if not Patient.objects.filter(NSS=patient_nss).exists():
            return ResultatLabo.objects.none()  # Alternatively, raise a 404 error

        history = ResultatLabo.objects.filter(
            examen__consultation__dossier__patient__NSS=patient_nss,
            examen__type='labo'
        ).select_related(
            'examen'
        ).prefetch_related(
            'healthmetrics_set'  # Updated to use default reverse relationship
        ).order_by('-dateAnalyse')
        return history
    

class ExaminationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsLaborantin]
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