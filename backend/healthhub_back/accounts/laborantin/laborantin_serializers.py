# serializers.py

from rest_framework import serializers
from healthhub_back.models import (
    Examen, ResultatLabo, HealthMetrics, Medicament, OrdonnanceMedicament,
    Medicament, Consultation, Medecin
)
from healthhub_back.accounts.patient.patient_serializers import HealthMetricsSerializer,ResultatLaboSerializer


from django.utils import timezone


class ExamRequiredSerializer(serializers.ModelSerializer):
    doctor_details = serializers.CharField(read_only=True)
    patient = serializers.CharField(source='consultation.dossier.patient.__str__', read_only=True)
    patient_id = serializers.CharField(source='consultation.dossier.patient.user.id', read_only=True)
    nss = serializers.CharField(source='consultation.dossier.patient.NSS', read_only=True)
    type = serializers.CharField(source='get_type_display', read_only=True)
    etat = serializers.CharField(source='get_etat_display', read_only=True)
    priorite = serializers.CharField(source='get_priorite_display', read_only=True)
    # Include 'doctor_details' from Examen model
    # Conditionally include 'health_metrics' if 'etat' is 'termine'
    health_metrics = serializers.SerializerMethodField()

    class Meta:
        model = Examen
        fields = [
            'examenID',
            'consultation',
            'patient',
            'patient_id',
            'type',
            'etat',
            'priorite',
            'doctor_details',
            'createdAt',
            'health_metrics',  
            'nss'
        ]

    def get_health_metrics(self, obj):
        if obj.etat == 'termine':
            # Assuming each 'termine' exam has at most one ResultatLabo
            try:
                resultat_labo = obj.resultatlabo_set.first()
                if resultat_labo:
                    return HealthMetricsSerializer(resultat_labo.healthmetrics_set.all(), many=True).data
            except ResultatLabo.DoesNotExist:
                return []
        return []  # Return empty list if not 'termine'



class HealthMetricsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetrics
        fields = ['metric_type', 'value', 'unit']

class ResultatLaboCreateSerializer(serializers.ModelSerializer):
    health_metrics = HealthMetricsCreateSerializer(many=True)

    class Meta:
        model = ResultatLabo
        fields = ['examen', 'resultat', 'status', 'health_metrics']

    def create(self, validated_data):
        health_metrics_data = validated_data.pop('health_metrics')
        laboratin = self.context.get('laboratin')
        if not laboratin:
            raise serializers.ValidationError("Laborantin context is required.")

        resultat_labo = ResultatLabo.objects.create(
            laboratin=laboratin,
            dateAnalyse=timezone.now(),
            **validated_data
        )
        for metric_data in health_metrics_data:
            HealthMetrics.objects.create(resLabo=resultat_labo, **metric_data)
        return resultat_labo


class ResultatLaboHistorySerializer(serializers.ModelSerializer):
    health_metrics = HealthMetricsSerializer(many=True, read_only=True,source='healthmetrics_set')
    examenID = serializers.UUIDField(source='examen.examenID', read_only=True)
    examen_type = serializers.CharField(source='examen.get_type_display', read_only=True)
    dateAnalyse = serializers.DateField()

    class Meta:
        model = ResultatLabo
        fields = [
            'resLaboID',
            'examenID',
            'examen_type',
            'resultat',
            'dateAnalyse',
            'status',
            'health_metrics'
        ]

class LabResultHistorySerializer(serializers.ModelSerializer):
    health_metrics = HealthMetricsSerializer(many=True, read_only=True)
    examenID = serializers.CharField(source='examen.examenID', read_only=True)
    examen_type = serializers.CharField(source='examen.get_type_display', read_only=True)
    dateAnalyse = serializers.DateField()

    class Meta:
        model = ResultatLabo
        fields = [
            'resLaboID',
            'examenID',
            'examen_type',
            'resultat',
            'dateAnalyse',
            'status',
            'health_metrics'
        ]