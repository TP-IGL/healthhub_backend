# laborantin_views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from healthhub_back.models import Examen, ResultatLabo, HealthMetrics, Laboratin

from .laborantin_serializers import (
    LaborantinExaminationListSerializer,
    ResultatLaboCreateUpdateSerializer,
    LaborantinStatisticsSerializer,
    PatientLabHistorySerializer,
    HealthMetricCreateSerializer
)

from rest_framework import permissions

class IsLaborantin(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role == 'laborantin' or request.user.role == 'admin'  

class LaborantinExaminationListView(generics.ListAPIView):
    """List all laboratory examinations for the lab technician"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = LaborantinExaminationListSerializer

    def get_queryset(self):
        queryset = Examen.objects.filter(
            type='labo',
            consultation__dossier__patient__centreHospitalier=self.request.user.centreHospitalier
        ).select_related(
            'consultation__dossier__patient',
            'consultation__dossier__patient__medecin__user'
        )

        # Apply filters
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(etat=status)
        if priority:
            queryset = queryset.filter(priorite=priority)
        if start_date and end_date:
            queryset = queryset.filter(createdAt__range=[start_date, end_date])

        return queryset

class LaborantinExaminationDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific examination"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = PatientLabHistorySerializer
    lookup_field = 'examenID'

    def get_queryset(self):
        return Examen.objects.filter(
            type='labo',
            consultation__dossier__patient__centreHospitalier=self.request.user.centreHospitalier
        ).select_related(
            'consultation__dossier__patient',
            'consultation__dossier__patient__medecin__user'
        ).prefetch_related(
            'resultatlabo_set__health_metrics'
        )

class ResultatLaboCreateView(generics.CreateAPIView):
    """Create new laboratory results"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = ResultatLaboCreateUpdateSerializer

    def perform_create(self, serializer):
        examen = get_object_or_404(Examen, examenID=self.kwargs['examenID'])

        if examen.consultation.dossier.patient.centreHospitalier != self.request.user.centreHospitalier:
            raise PermissionDenied("Not authorized for this hospital's examinations")

        laboratin = get_object_or_404(Laboratin, user=self.request.user)
        serializer.save(
            examen=examen,
            laboratin=laboratin
        )

        # Update examination status
        examen.etat = 'termine'
        examen.save()

        # Update technician's test count
        laboratin.nombreTests += 1
        laboratin.save()

class ResultatLaboUpdateView(generics.UpdateAPIView):
    """Update existing laboratory results"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = ResultatLaboCreateUpdateSerializer
    lookup_field = 'resLaboID'

    def get_queryset(self):
        return ResultatLabo.objects.filter(
            laboratin__user=self.request.user
        )

class HealthMetricCreateView(generics.CreateAPIView):
    """Add new health metrics to results"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = HealthMetricCreateSerializer

    def perform_create(self, serializer):
        resultat_labo = get_object_or_404(
            ResultatLabo,
            resLaboID=self.kwargs['resLaboID'],
            laboratin__user=self.request.user
        )
        serializer.save(
            resLabo=resultat_labo,
            medical_record_id=resultat_labo.examen.consultation.dossier.dossierID,
            recorded_by=self.request.user.id
        )

class LaborantinStatisticsView(generics.RetrieveAPIView):
    """Get lab technician statistics"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = LaborantinStatisticsSerializer

    def get_object(self):
        laboratin = get_object_or_404(Laboratin, user=self.request.user)

        # Calculate statistics
        results = ResultatLabo.objects.filter(laboratin=laboratin)

        # Tests by status
        tests_by_status = results.values('status').annotate(
            count=Count('resLaboID')
        )

        # Tests by priority
        tests_by_priority = results.values(
            'examen__priorite'
        ).annotate(
            count=Count('resLaboID')
        )

        # Average processing time
        avg_time = results.aggregate(
            avg_time=Avg(F('dateAnalyse') - F('examen__createdAt'))
        )['avg_time']

        # Add calculated fields
        laboratin.total_tests = results.count()
        laboratin.tests_by_status = {
            item['status']: item['count'] for item in tests_by_status
        }
        laboratin.tests_by_priority = {
            item['examen__priorite']: item['count'] for item in tests_by_priority
        }
        laboratin.average_processing_time = avg_time or timedelta(0)

        return laboratin

class PatientLabHistoryView(generics.ListAPIView):
    """Get patient's laboratory history"""
    permission_classes = [IsAuthenticated, IsLaborantin]
    serializer_class = PatientLabHistorySerializer

    def get_queryset(self):
        return Examen.objects.filter(
            type='labo',
            consultation__dossier__patient__user_id=self.kwargs['patient_id'],
            consultation__dossier__patient__centreHospitalier=self.request.user.centreHospitalier
        ).select_related(
            'consultation__dossier__patient'
        ).prefetch_related(
            'resultatlabo_set__health_metrics'
        )