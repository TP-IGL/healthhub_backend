from rest_framework import serializers
from healthhub_back.models import (
    Patient,
    DossierMedical,
    Consultation,
    Ordonnance,
    OrdonnanceMedicament,
    Medicament,
    Examen,
    ResultatLabo,
    ResultatRadio,
    HealthMetrics,
    ActiviteInfermier,
)

from django_filters import rest_framework as filters

class PatientSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for basic patient details.
    """
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'NSS']


class NurseMedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['medicamentID', 'nom', 'type', 'description']


class NurseOrdonnanceMedicamentSerializer(serializers.ModelSerializer):
    medicament = NurseMedicamentSerializer(read_only=True)
    medicament_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrdonnanceMedicament
        fields = [
            'ordonnanceMedicamentID',
            'medicament',
            'medicament_id',
            'duree',
            'dosage',
            'frequence',
            'instructions'
        ]


class NurseOrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = NurseOrdonnanceMedicamentSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = [
            'ordonnanceID',
            'valide',
            'dateCreation',
            'dateExpiration',
            'medicaments'
        ]


class NurseExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = [
            'examenID',
            'type',
            'notes',
            'etat',
            'priorite',
            'createdAt'
        ]


class NurseConsultationSerializer(serializers.ModelSerializer):
    ordonnance = NurseOrdonnanceSerializer(read_only=True)
    complementary_exams = NurseExamenSerializer(many=True, read_only=True, source='examen_set')
    # Include results and health metrics if needed
    # For simplicity, omitted here

    class Meta:
        model = Consultation
        fields = [
            'consultationID',
            'dossier',
            'dateConsultation',
            'diagnostic',
            'resume',
            'status',
            'ordonnance',
            'complementary_exams'
        ]

    def get_patient(self, obj):
        """
        Retrieves patient details from the related DossierMedical model.
        """
        patient = obj.dossier.patient
        return PatientSummarySerializer(patient).data
    

class ValidateActiviteSerializer(serializers.Serializer):
    nurse_observations = serializers.CharField(max_length=500)



class ActivitySerializer(serializers.ModelSerializer):
    typeActivite = serializers.CharField(source="get_typeActivite_display")
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ActiviteInfermier
        fields = [
            "id",
            "typeActivite",
            "status",
            "doctors_details",
            "nurse_observations",
            # "details",
            "createdAt",
        ]

class PatientNurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["nom", "prenom", "NSS"]

class NurseConsultationDetailSerializer(serializers.Serializer):
    patient = PatientNurseSerializer()  # Patient details
    activities = ActivitySerializer(many=True)  # Activities related to the patient
    consultation = NurseConsultationSerializer()  # Related consultation







