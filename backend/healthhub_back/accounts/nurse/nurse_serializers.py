from rest_framework import serializers
from healthhub_back.models import (
    Patient,
    Consultation,
    Ordonnance,
    OrdonnanceMedicament,
    Medicament,
    Examen,
    ActiviteInfermier,
)


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


class NurseActivitySerializer(serializers.ModelSerializer):
    ordonnance = NurseOrdonnanceSerializer(read_only=True)
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

class NurseActivityDetailSerializer(serializers.Serializer):
    patient = PatientNurseSerializer()  # Patient details
    activities = ActivitySerializer(many=True)  # Activities related to the patient
    consultation = NurseActivitySerializer()  # Related consultation







