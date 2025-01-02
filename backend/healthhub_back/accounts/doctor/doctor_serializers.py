from rest_framework import serializers
from healthhub_back.models import (
    ActiviteInfermier,
    Infermier,
    Patient,
    DossierMedical,
    Consultation,
    Ordonnance,
    OrdonnanceMedicament,
    Medicament,
    Examen,
    ResultatLabo,
    ResultatRadio,
    Consultation, 
    DossierMedical,
    HealthMetrics,
    Radiologue,
    Laboratin,
    Ordonnance, 
    OrdonnanceMedicament, 
    Medicament
)
from django.db import transaction

from django.contrib.auth import get_user_model
from django.utils import timezone
from healthhub_back.accounts.patient.patient_serializers import ExamensSerializer


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
            'doctor_details',
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
        'patientID': str(patient.user.id),  # Now using user.id as patientID
        'NSS': patient.NSS,
        'nom': patient.nom,
        'prenom': patient.prenom,
        'dateNaissance': patient.dateNaissance,
        'adresse': patient.adresse,
        'telephone': patient.telephone,
        'email': patient.user.email,
        'mutuelle': patient.mutuelle,
        'contactUrgence': patient.contactUrgence,
        'createdAt': patient.createdAt,
    }


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class PatientSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['user', 'NSS', 'nom', 'prenom', 'dateNaissance', 'adresse', 
                 'telephone', 'mutuelle', 'contactUrgence', 'createdAt']

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




class ConsultationCreateUpdateSerializer(serializers.ModelSerializer):
    nss = serializers.IntegerField(write_only=True)

    class Meta:
        model = Consultation
        fields = ['consultationID', 'nss', 'dateConsultation', 
                  'diagnostic', 'resume', 'status']
        read_only_fields = ['consultationID', 'dateConsultation']  

    def validate_nss(self, value):
        try:
            DossierMedical.objects.get(patient__NSS=value)
            return value
        except DossierMedical.DoesNotExist:
            raise serializers.ValidationError("Patient medical file not found")

    def create(self, validated_data):
        nss = validated_data.pop('nss')
        dossier = DossierMedical.objects.get(patient__NSS=nss)
        # Set dateConsultation to current time
        validated_data['dateConsultation'] = timezone.now().date()
        return Consultation.objects.create(dossier=dossier, **validated_data)

    

class ExaminationCreateSerializer(serializers.ModelSerializer):
    radiologue_id = serializers.UUIDField(required=False, write_only=True)
    laborantin_id = serializers.UUIDField(required=False, write_only=True)

    class Meta:
        model = Examen
        fields = ['type', 'priorite', 'doctor_details', 
                 'radiologue_id', 'laborantin_id']

    def validate(self, data):
        if data['type'] == 'radio':
            if 'radiologue_id' not in data:
                raise serializers.ValidationError(
                    "radiologue_id is required for radio examinations"
                )
            try:
                data['radiologue'] = Radiologue.objects.get(
                    user_id=data.pop('radiologue_id')
                )
            except Radiologue.DoesNotExist:
                raise serializers.ValidationError("Invalid radiologue_id")

        elif data['type'] == 'labo':
            if 'laborantin_id' not in data:
                raise serializers.ValidationError(
                    "laborantin_id is required for laboratory examinations"
                )
            try:
                data['laborantin'] = Laboratin.objects.get(
                    user_id=data.pop('laborantin_id')
                )
            except Laboratin.DoesNotExist:
                raise serializers.ValidationError("Invalid laborantin_id")
        return data

class RadiologueListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username')

    class Meta:
        model = Radiologue
        fields = ['user_id', 'name', 'specialite', 'shift', 'nombreTests']

class LaborantinListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username')

    class Meta:
        model = Laboratin
        fields = ['user_id', 'name', 'specialite', 'shift', 'nombreTests']

class InfermierListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username')

    class Meta:
        model = Infermier
        fields = ['user_id', 'name', 'shift']
#### Prescription


class MedicamentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['nom', 'type', 'description']

class OrdonnanceMedicamentCreateSerializer(serializers.ModelSerializer):
    medicament_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrdonnanceMedicament
        fields = [
            'medicament_id',
            'duree',
            'dosage',
            'frequence',
            'instructions'
        ]

class OrdonnanceCreateSerializer(serializers.ModelSerializer):
    medicaments = OrdonnanceMedicamentCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Ordonnance
        fields = ['dateExpiration', 'medicaments']

    def create(self, validated_data):
        medicaments_data = validated_data.pop('medicaments')
        ordonnance = Ordonnance.objects.create(**validated_data)

        for medicament_data in medicaments_data:
            medicament_id = medicament_data.pop('medicament_id')
            medicament = Medicament.objects.get(medicamentID=medicament_id)
            OrdonnanceMedicament.objects.create(
                ordonnance=ordonnance,
                med=medicament,
                **medicament_data
            )

        return ordonnance

class OrdonnanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ['valide']



class MedicationInputSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=Medicament.TYPE_CHOICES)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    dosage = serializers.ChoiceField(choices=[
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('fort', 'Fort'),
    ])
    duree = serializers.CharField(max_length=50)
    frequence = serializers.CharField(max_length=50)
    instructions = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate(self, attrs):
        # Ensure that for existing medications, description is not required
        if 'description' not in attrs or not attrs['description']:
            # Check if the medication already exists
            if not Medicament.objects.filter(nom=attrs['nom'], type=attrs['type']).exists():
                raise serializers.ValidationError({
                    "description": "Description is required for new medications."
                })
        return attrs
    


class PrescriptionCreateSerializer(serializers.Serializer):
    medications = MedicationInputSerializer(many=True)

    def validate_medications(self, value):
        if not value:
            raise serializers.ValidationError("At least one medication must be provided.")
        return value

    def create(self, validated_data):
        medications_data = validated_data.pop('medications')
        consultation = self.context.get('consultation')

        if not consultation:
            raise serializers.ValidationError("Consultation context is required.")

        with transaction.atomic():
            # Create the Ordonnance
            ordonnance = Ordonnance.objects.create(
                consultation=consultation,
                valide=False,  # or set based on your requirements
                dateExpiration=None  # You may set this based on your logic
            )

            for med_data in medications_data:
                nom = med_data.get('nom')
                type_ = med_data.get('type')
                description = med_data.get('description', '')

                # Get or create Medicament
                medicament, created = Medicament.objects.get_or_create(
                    nom=nom,
                    type=type_,
                    defaults={'description': description}
                )
                if not created and not medicament.description:
                    # Update description if it was previously blank and now provided
                    medicament.description = description
                    medicament.save()

                # Create OrdonnanceMedicament
                OrdonnanceMedicament.objects.create(
                    med=medicament,
                    ordonnance=ordonnance,
                    duree=med_data.get('duree'),
                    dosage=med_data.get('dosage'),
                    frequence=med_data.get('frequence'),
                    instructions=med_data.get('instructions', '')
                )

            return ordonnance
        

class ActiviteInfermierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiviteInfermier
        fields = ['consultation', 'infermier', 'typeActivite', 'doctors_details', 'status']