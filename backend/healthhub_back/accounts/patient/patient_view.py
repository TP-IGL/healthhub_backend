# views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from healthhub_back.models import Patient, DossierMedical
from .patient_serializers import DossierMedicalDetailSerializer
from rest_framework.views import APIView


class PatientMedicalFileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DossierMedicalDetailSerializer

    def get_queryset(self):
        return DossierMedical.objects.select_related(
            'patient',
            'patient__medecin',
            'patient__medecin__user',
            'patient__centreHospitalier'
        ).prefetch_related(
            'consultation_set',
            'consultation_set__ordonnance_set',
            'consultation_set__ordonnance_set__ordonnancemedicament_set',
            'consultation_set__ordonnance_set__ordonnancemedicament_set__med',
            'consultation_set__examen_set',
            'consultation_set__examen_set__resultatlabo_set',
            'consultation_set__examen_set__resultatlabo_set__healthmetrics_set',
            'consultation_set__examen_set__resultatradio_set',
            'consultation_set__activiteinfermier_set',
            'consultation_set__activiteinfermier_set__infermier'
        )

    def get(self, request, patient_id):
        if not self.has_permission_to_access(request.user, patient_id):
            return Response(
                {"error": "You don't have permission to access this medical file"},
                status=status.HTTP_403_FORBIDDEN
            )

        dossier = get_object_or_404(
            self.get_queryset(), 
            patient__user__id=patient_id
        )
        serializer = self.serializer_class(dossier)
        return Response(serializer.data)

    def has_permission_to_access(self, user, patient_id):
        # If user is the patient
        if user.id == patient_id:
            return True
        if user.role == 'admin':
            return True
        # If user is medical staff from the same hospital
        if user.role in ['medecin', 'infermier', 'pharmacien', 'laborantin', 'radiologue', 'admin']:
            patient = get_object_or_404(Patient, user__id=patient_id)
            return user.centreHospitalier == patient.centreHospitalier 

        return False

class RetrieveQRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        # Fetch the dossier associated with the patient
        dossier = get_object_or_404(DossierMedical, patient__user__id=patient_id)

        # Check permissions
        if not self.has_permission_to_access(request.user, dossier.patient.user.id):
            return Response(
                {"error": "You don't have permission to access this QR code"},
                status=403
            )

        # Return the QR code
        return Response({"qrCode": dossier.qrCode})

    def has_permission_to_access(self, user, patient_id):
        # If user is the patient
        if user.id == patient_id:
            return True
        if user.role == 'admin':
            return True
        # If user is medical staff from the same hospital
        if user.role in ['medecin', 'infermier', 'pharmacien', 'laborantin', 'radiologue', 'admin']:
            patient = get_object_or_404(Patient, user__id=patient_id)
            return user.centreHospitalier == patient.centreHospitalier 

        return False
    
class RetrieveQRCodeViewNSS(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nss):
        # Fetch the dossier associated with the patient using their NSS
        dossier = get_object_or_404(DossierMedical, patient__NSS=nss)

        # Check permissions
        if not self.has_permission_to_access(request.user, dossier.patient.user.id):
            return Response(
                {"error": "You don't have permission to access this QR code"},
                status=403
            )

        # Return the QR code
        return Response({"qrCode": dossier.qrCode})

    def has_permission_to_access(self, user, patient_id):
        # If user is the patient
        if user.id == patient_id:
            return True
        if user.role == 'admin':
            return True
        # If user is medical staff from the same hospital
        if user.role in ['medecin', 'infermier', 'pharmacien', 'laborantin', 'radiologue', 'admin']:
            patient = get_object_or_404(Patient, user__id=patient_id)
            return user.centreHospitalier == patient.centreHospitalier 

        return False


''' Example output : 
{
    "dossierID": "uuid-value",
    "patient": {
        "NSS": "123456789",
        "nom": "Doe",
        "prenom": "John",
        "dateNaissance": "1990-01-01T00:00:00Z",
        "adresse": "123 Main St",
        "telephone": "123-456-7890",
        "mutuelle": "Insurance Company",
        "contactUrgence": "Jane Doe: 123-456-7890",
        "medecin": {
            "specialite": "generaliste",
            "telephone": "123-456-7890",
            "user": {
                "username": "dr.smith",
                "first_name": "John",
                "last_name": "Smith"
            }
        },
        "centre_hospitalier": {
            "id": 1,
            "nom": "Hospital Name",
            "place": "City"
        },
        "createdAt": "2024-01-01T00:00:00Z"
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "active": true,
    "consultations": [
        {
            "consultationID": "uuid-value",
            "dateConsultation": "2024-01-01T10:00:00Z",
            "diagnostic": "Patient diagnosis",
            "resume": "Consultation summary",
            "status": "termine",
            "medecin_name": "Dr. John Smith",
            "ordonnances": [
                {
                    "ordonnanceID": "uuid-value",
                    "valide": true,
                    "dateCreation": "2024-01-01T10:30:00Z",
                    "dateExpiration": "2024-02-01T10:30:00Z",
                    "medicaments": [
                        {
                            "ordonnanceMedicamentID": "uuid-value",
                            "medicament": {
                                "medicamentID": "uuid-value",
                                "nom": "Medicine Name",
                                "type": "comprime",
                                "description": "Medicine description"
                            },
                            "duree": "7 days",
                            "dosage": "moyen",
                            "frequence": "3 times per day",
                            "instructions": "Take with food"
                        }
                    ]
                }
            ],
            "examens": [
                {
                    "examenID": "uuid-value",
                    "type": "radio",
                    "doctor_details": "Doctor's notes",
                    "medecin_name": "Dr. John Smith",
                    "createdAt": "2024-01-01T11:00:00Z",
                    "etat": "termine",
                    "priorite": "normal",
                    "resultat_radio": [
                        {
                            "resRadioID": "uuid-value",
                            "radiologue_name": "Dr. Jane Doe",
                            "radiologue_specialite": "Scanner",
                            "radioImgURL": "https://example.com/image.jpg",
                            "type": "scanner",
                            "rapport": "Radiology report",
                            "dateRealisation": "2024-01-01T14:00:00Z"
                        }
                    ],
                    "resultat_labo": [
                        {
                            "resLaboID": "uuid-value",
                            "laboratin_name": "Lab Tech Name",
                            "laboratin_specialite": "Biochimie",
                            "resultat": "Lab results",
                            "dateAnalyse": "2024-01-01T13:00:00Z",
                            "status": "termine",
                            "health_metrics": [
                                {
                                    "id": 1,
                                    "metric_type": "temperature",
                                    "value": "37.5",
                                    "unit": "°C",
                                    "measured_at": "2024-01-01T13:30:00Z"
                                }
                            ]
                        }
                    ]
                }
            ],
            "activites_infermier": [
                {
                    "id": "uuid-value",
                    "infermier_name": "Nurse Name",
                    "typeActivite": "administration_medicament",
                    "doctors_details": "Doctor's instructions",
                    "nurse_observations": "Nurse's notes",
                    "createdAt": "2024-01-01T15:00:00Z",
                    "status": "termine"
                }
            ]
        }
    ]
}
'''