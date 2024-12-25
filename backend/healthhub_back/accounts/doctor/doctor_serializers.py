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
)
from django.contrib.auth import get_user_model

User = get_user_model()


class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['medicamentID', 'nom', 'type', 'description']


class OrdonnanceMedicamentSerializer(serializers.ModelSerializer):
    medicament = MedicamentSerializer(read_only=True)
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


class OrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = OrdonnanceMedicamentSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = [
            'ordonnanceID',
            'valide',
            'dateCreation',
            'dateExpiration',
            'medicaments'
        ]


class ExamenSerializer(serializers.ModelSerializer):
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


class ConsultationSerializer(serializers.ModelSerializer):
    ordonnance = OrdonnanceSerializer(read_only=True)
    complementary_exams = ExamenSerializer(many=True, read_only=True, source='examen_set')
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


class ConsultationCreateSerializer(serializers.ModelSerializer):
    diagnostic = serializers.CharField(required=False, allow_blank=True)
    ordonnance = OrdonnanceMedicamentSerializer(many=True, write_only=True, required=False)
    complementary_exams = serializers.DictField(write_only=True, required=False)
    patient_query = serializers.CharField(write_only=True)

    class Meta:
        model = Consultation
        fields = [
            'consultationID',
            'dateConsultation',
            'diagnostic',
            'resume',
            'status',
            'ordonnance',
            'complementary_exams',
            'patient_query'
        ]
        read_only_fields = ['consultationID', 'status']

    def create(self, validated_data):
        ordonnance_data = validated_data.pop('ordonnance', [])
        complementary_exams = validated_data.pop('complementary_exams', {})
        patient_query = validated_data.pop('patient_query')

        from .doctor_service import search_patient, create_consultation

        user = self.context['request'].user
        medecin = user.medecin  # Assuming User has a related medecin object

        patient = search_patient(patient_query)
        consultation = create_consultation(medecin, patient, validated_data)
        return consultation


class ConsultationSummarySerializer(serializers.ModelSerializer):
    dossier = serializers.StringRelatedField()
    patient = serializers.SerializerMethodField()
    ordonnance = OrdonnanceSerializer(read_only=True)
    complementary_exams = ExamenSerializer(many=True, read_only=True, source='examen_set')

    class Meta:
        model = Consultation
        fields = [
            'consultationID',
            'dossier',
            'patient',
            'dateConsultation',
            'diagnostic',
            'resume',
            'status',
            'ordonnance',
            'complementary_exams'
        ]

    def get_patient(self, obj):
        patient = obj.dossier.patient
        return {
            'patientID': patient.patientID,
            'NSS': patient.NSS,
            'nom': patient.nom,
            'prenom': patient.prenom,
            'dateNaissance': patient.dateNaissance,
            'adresse': patient.adresse,
            'telephone': patient.telephone,
            'email': patient.email,
            'mutuelle': patient.mutuelle,
            'contactUrgence': patient.contactUrgence,
            'createdAt': patient.createdAt,
        }


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'patientID',
            'NSS',
            'nom',
            'prenom',
            'dateNaissance',
            'adresse',
            'telephone',
            'email',
            'mutuelle',
            'contactUrgence',
            'createdAt'
        ]


class DossierMedicalSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    consultations = ConsultationSerializer(many=True, read_only=True, source='consultation_set')

    class Meta:
        model = DossierMedical
        fields = [
            'dossierID',
            'patient',
            'createdAt',
            'active',
            'qrCode',
            'consultations'
        ]