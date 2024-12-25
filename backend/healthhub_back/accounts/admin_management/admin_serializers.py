from rest_framework import serializers
from django.contrib.auth import get_user_model
from healthhub_back.models import CentreHospitalier, DossierMedical, Medecin, Patient  # Update if necessary

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
User = get_user_model()


# Handles user creation, ensuring required fields like password are secure and validating the role field.
class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    role = serializers.ChoiceField(choices=User.USER_ROLES)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'centreHospitalier')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            centreHospitalier=validated_data.get('centreHospitalier')
        )
        return user

# Used to serialize and deserialize User objects for generic use
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'centreHospitalier')


class CentreHospitalierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreHospitalier
        fields = ('id', 'nom', 'place')

# serializers.py


# serializers.py
class PatientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Patient
        fields = ['username', 'email', 'password', 'NSS', 'nom', 'prenom', 
                 'dateNaissance', 'adresse', 'telephone', 'mutuelle', 
                 'contactUrgence', 'medecin', 'centreHospitalier']

    def validate_medecin(self, value):
        if value:
            try:
                medecin = Medecin.objects.get(user=value.user)
                return medecin
            except Medecin.DoesNotExist:
                raise serializers.ValidationError("Le médecin spécifié n'existe pas.")
        return None

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email existe déjà.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà.")
        return value

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['patientID', 'NSS', 'nom', 'prenom', 'dateNaissance', 'adresse', 
                 'telephone', 'email', 'mutuelle', 'contactUrgence', 'medecin', 
                 'centreHospitalier', 'createdAt']
        read_only_fields = ['patientID', 'createdAt']

class DossierMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = ['dossierID', 'patient', 'createdAt', 'active', 'qrCode']
        read_only_fields = ['dossierID', 'qrCode']