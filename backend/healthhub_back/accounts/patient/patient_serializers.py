# serializers.py

from rest_framework import serializers
from healthhub_back.models import (
    Patient, DossierMedical, Consultation, Ordonnance, 
    OrdonnanceMedicament, Medicament, ActiviteInfermier,
    Examen, ResultatLabo, ResultatRadio, HealthMetrics,
    CentreHospitalier, Medecin
)

class CentresHospitalierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreHospitalier
        fields = ['id', 'nom', 'place']

class MedecinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medecin
        fields = ['specialite', 'telephone', 'user']

class MedicamentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['medicamentID', 'nom', 'type', 'description']

class OrdonnancesMedicamentSerializer(serializers.ModelSerializer):
    medicament = MedicamentsSerializer(source='med', read_only=True)

    class Meta:
        model = OrdonnanceMedicament
        fields = [
            'ordonnanceMedicamentID',
            'medicament',
            'duree',
            'dosage',
            'frequence',
            'instructions'
        ]

class OrdonnancesSerializer(serializers.ModelSerializer):
    medicaments = OrdonnancesMedicamentSerializer(
        source='ordonnancemedicament_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Ordonnance
        fields = [
            'ordonnanceID',
            'valide',
            'dateCreation',
            'dateExpiration',
            'medicaments'
        ]

class HealthMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetrics
        fields = ['id', 'metric_type', 'value', 'unit', 'measured_at']

class ResultatLaboSerializer(serializers.ModelSerializer):
    laboratin_name = serializers.CharField(source='laboratin.__str__', read_only=True)
    laboratin_specialite = serializers.CharField(source='laboratin.specialite', read_only=True)
    health_metrics = HealthMetricsSerializer(many=True, read_only=True)

    class Meta:
        model = ResultatLabo
        fields = [
            'resLaboID',
            'laboratin_name',
            'laboratin_specialite',
            'resultat',
            'dateAnalyse',
            'status',
            'health_metrics'
        ]

class ResultatsRadioSerializer(serializers.ModelSerializer):
    radiologue_name = serializers.CharField(source='examen.radiologue.__str__', read_only=True)
    radiologue_specialite = serializers.CharField(source='examen.radiologue.specialite', read_only=True)

    class Meta:
        model = ResultatRadio
        fields = [
            'resRadioID',
            'radiologue_name',
            'radiologue_specialite',
            'radioImgURL',
            'type',
            'rapport',
            'dateRealisation'
        ]

class ExamensSerializer(serializers.ModelSerializer):
    resultat_labo = ResultatLaboSerializer(source='resultatlabo_set', many=True, read_only=True)
    resultat_radio = ResultatsRadioSerializer(source='resultatradio_set', many=True, read_only=True)
    medecin_name = serializers.CharField(
        source='consultation.dossier.patient.medecin.__str__', 
        read_only=True
    )

    class Meta:
        model = Examen
        fields = [
            'examenID',
            'type',
            'doctor_details',
            'medecin_name',
            'createdAt',
            'etat',
            'priorite',
            'resultat_labo',
            'resultat_radio'
        ]

class ActiviteInfermierSerializer(serializers.ModelSerializer):
    infermier_name = serializers.CharField(source='infermier.__str__', read_only=True)

    class Meta:
        model = ActiviteInfermier
        fields = [
            'id',
            'infermier_name',
            'typeActivite',
            'doctors_details',
            'nurse_observations',
            'createdAt',
            'status'
        ]

class ConsultationsSerializer(serializers.ModelSerializer):
    ordonnances = OrdonnancesSerializer(source='ordonnance_set', many=True, read_only=True)
    examens = ExamensSerializer(source='examen_set', many=True, read_only=True)
    activites_infermier = ActiviteInfermierSerializer(
        source='activiteinfermier_set',
        many=True,
        read_only=True
    )
    medecin_name = serializers.CharField(
        source='dossier.patient.medecin.__str__', 
        read_only=True
    )

    class Meta:
        model = Consultation
        fields = [
            'consultationID',
            'dateConsultation',
            'diagnostic',
            'resume',
            'status',
            'medecin_name',
            'ordonnances',
            'examens',
            'activites_infermier'
        ]

class PatientsSerializer(serializers.ModelSerializer):
    medecin = MedecinSerializer(read_only=True)
    centre_hospitalier = CentresHospitalierSerializer(source='centreHospitalier', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'NSS',
            'nom',
            'prenom',
            'dateNaissance',
            'adresse',
            'telephone',
            'mutuelle',
            'contactUrgence',
            'medecin',
            'centre_hospitalier',
            'createdAt'
        ]

class DossierMedicalDetailSerializer(serializers.ModelSerializer):
    patient = PatientsSerializer(read_only=True)
    consultations = ConsultationsSerializer(source='consultation_set', many=True, read_only=True)

    class Meta:
        model = DossierMedical
        fields = ['dossierID', 'patient', 'createdAt', 'active', 'consultations']