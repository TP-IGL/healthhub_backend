# laborantin_serializers.py
from rest_framework import serializers
from healthhub_back.models import Examen, ResultatLabo, HealthMetrics, Laboratin
from healthhub_back.accounts.patient.patient_serializers import PatientsSerializer, HealthMetricsSerializer,ResultatLaboSerializer

class LaborantinExaminationListSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor_name = serializers.CharField(
        source='consultation.dossier.patient.medecin.__str__',
        read_only=True
    )

    class Meta:
        model = Examen
        fields = [
            'examenID',
            'patient',
            'doctor_name',
            'doctor_details',
            'type',
            'createdAt',
            'etat',
            'priorite'
        ]

    def get_patient(self, obj):
        return {
            'nom': obj.consultation.dossier.patient.nom,
            'prenom': obj.consultation.dossier.patient.prenom,
            'NSS': obj.consultation.dossier.patient.NSS
        }

class HealthMetricCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetrics
        fields = ['metric_type', 'value', 'unit']

class ResultatLaboCreateUpdateSerializer(serializers.ModelSerializer):
    health_metrics = HealthMetricCreateSerializer(many=True, required=False)

    class Meta:
        model = ResultatLabo
        fields = ['resultat', 'dateAnalyse', 'status', 'health_metrics']

    def create(self, validated_data):
        health_metrics_data = validated_data.pop('health_metrics', [])
        resultat_labo = ResultatLabo.objects.create(**validated_data)

        for metric_data in health_metrics_data:
            HealthMetrics.objects.create(
                resLabo=resultat_labo,
                medical_record_id=resultat_labo.examen.consultation.dossier.dossierID,
                recorded_by=resultat_labo.laboratin.user.id,
                **metric_data
            )

        return resultat_labo

class LaborantinStatisticsSerializer(serializers.ModelSerializer):
    total_tests = serializers.IntegerField(read_only=True)
    tests_by_status = serializers.DictField(read_only=True)
    tests_by_priority = serializers.DictField(read_only=True)
    average_processing_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Laboratin
        fields = [
            'nombreTests',
            'total_tests',
            'tests_by_status',
            'tests_by_priority',
            'average_processing_time'
        ]

class PatientLabHistorySerializer(serializers.ModelSerializer):
    patient_info = PatientsSerializer(source='consultation.dossier.patient', read_only=True)
    results = ResultatLaboSerializer(source='resultatlabo_set', many=True, read_only=True)

    class Meta:
        model = Examen
        fields = [
            'examenID',
            'patient_info',
            'type',
            'doctor_details',
            'createdAt',
            'etat',
            'priorite',
            'results'
        ]