# accounts/admin_management/services.py

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from healthhub_back.models import DossierMedical, Patient
from .admin_serializers import AdminUserCreateSerializer, AdminUserSerializer
from django.contrib.auth.hashers import make_password
import qrcode
import base64
import io

User = get_user_model()

def create_user_account(data):
    serializer = AdminUserCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return user

def list_all_users():
    return User.objects.all()

def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValidationError('User not found.')

def update_user(user, data):
    serializer = AdminUserSerializer(user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data

def delete_user(user):
    user.delete()


from django.db import transaction

class PatientService:
    @staticmethod
    def create_patient_with_dossier(validated_data):
        with transaction.atomic():
            try:
                # Extract User-specific data
                user_data = {
                    'username': validated_data.pop('username'),
                    'email': validated_data.pop('email'),
                    'password': make_password(validated_data.pop('password')),
                    'first_name': validated_data.get('prenom'),
                    'last_name': validated_data.get('nom'),
                    'role': 'patient'
                }

                # Create User
                user = User.objects.create(**user_data)

                # Create Patient
                patient = Patient.objects.create(
                    user=user,
                    **validated_data
                )

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )

                qr_data = {
                    'patientID': str(patient.user.id),
                    'nom': patient.nom,
                    'prenom': patient.prenom,
                    'NSS': str(patient.NSS)
                }

                qr.add_data(str(qr_data))
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")

                # Convert QR code to base64 string
                buffer = io.BytesIO()
                qr_image.save(buffer, format="PNG")
                qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

                # Create dossier
                dossier = DossierMedical.objects.create(
                    patient=patient,
                    qrCode=qr_code_base64
                )

                return patient, dossier

            except Exception as e:
                raise ValidationError(f"Erreur lors de la création du patient et du dossier: {str(e)}")