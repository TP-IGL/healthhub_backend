from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from healthhub_back.models import (
    CentreHospitalier,
    Patient,
    Medecin,
    DossierMedical,
    Medicament,
    Consultation,
)
from rest_framework.authtoken.models import Token
from rest_framework import status

User = get_user_model()





class MedecinAPITestCase(APITestCase):
    def setUp(self):
        # Create Centre Hospitalier
        self.centre = CentreHospitalier.objects.create(nom='Centre A', place='Place A')

        # Create Médecin
        self.medecin_user = User.objects.create_user(
            username='medecin1',
            email='medecin1@example.com',
            password='medecinpass',
            role='medecin',
            centreHospitalier=self.centre
        )
        self.medecin = Medecin.objects.create(
            user=self.medecin_user,
            specialite='cardiologue',
            telephone='1234567890'
        )

        # Create Patient assigned to this Médecin
        self.patient = Patient.objects.create(
            NSS=123456789012,
            nom='Doe',
            prenom='John',
            dateNaissance='1990-01-01',
            adresse='123 Main St',
            telephone='0987654321',
            email='john.doe@example.com',
            mutuelle='Mutuelle A',
            contactUrgence='Jane Doe',
            medecin=self.medecin,
            centreHospitalier=self.centre,
            password='password123',
        )

        # Create DossierMedical for Patient
        self.dossier = DossierMedical.objects.create(
            patient=self.patient,
            qrCode='qr-code-1234',
            active=True,
        )

        # Create Medicament
        self.medicament = Medicament.objects.create(
            nom='Aspirin',
            type='comprime',
            description='Pain reliever'
        )

        # Obtain Token for Médecin
        self.token = Token.objects.create(user=self.medecin_user)
        self.auth_header = f'Token {self.token.key}'

    def test_search_patient_by_nss(self):
        url = reverse('search_and_retrieve_dossier')
        response = self.client.get(url, {'query': '123456789012'}, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['patient']['prenom'], 'John')
        self.assertEqual(response.data['patient']['nom'], 'Doe')
        self.assertEqual(response.data['qrCode'], 'qr-code-1234')
        self.assertIn('consultations', response.data)

    def test_search_patient_by_qr_code(self):
        url = reverse('search_and_retrieve_dossier')
        response = self.client.get(url, {'query': 'qr-code-1234'}, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['patient']['prenom'], 'John')
        self.assertEqual(response.data['patient']['nom'], 'Doe')
        self.assertEqual(response.data['qrCode'], 'qr-code-1234')
        self.assertIn('consultations', response.data)

    def test_create_consultation_with_ordonnance(self):
        url = reverse('create_consultation')
        data = {
            "patient_query": "123456789012",
            "dateConsultation": "2024-01-15",
            "diagnostic": "Hypertension",
            "resume": "Patient exhibits high blood pressure.",
            "ordonnance": [
                {
                    "medicament_id": str(self.medicament.medicamentID),
                    "duree": "2 weeks",
                    "dosage": "10mg",
                    "frequence": "Twice a day",
                    "instructions": "Take after meals."
                }
            ],
            "dateExpiration": "2024-02-15"
        }
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['diagnostic'], 'Hypertension')
        self.assertIsNotNone(response.data['ordonnance'])
        self.assertEqual(response.data['ordonnance']['valide'], True)
        self.assertEqual(len(response.data['ordonnance']['medicaments']), 1)

    def test_create_consultation_with_complementary_exams(self):
        url = reverse('create_consultation')
        data = {
            "patient_query": "qr-code-1234",
            "dateConsultation": "2024-01-16",
            "resume": "Difficulty in establishing diagnosis.",
            "complementary_exams": {
                "bilan_biologique": [
                    {
                        "notes": "Request blood sugar levels.",
                        "priorite": "urgent"
                    }
                ],
                "bilan_radiologique": [
                    {
                        "notes": "Request chest X-ray.",
                        "priorite": "normal"
                    }
                ]
            }
        }
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['diagnostic'], '')
        self.assertIsNone(response.data['ordonnance'])
        self.assertIn('complementary_exams', response.data)
        self.assertEqual(len(response.data['complementary_exams']), 2)

    def test_visualize_medical_record(self):
        # First, create a consultation
        consultation = Consultation.objects.create(
            dossier=self.dossier,
            dateConsultation="2024-01-15",
            diagnostic="Hypertension",
            resume="Patient exhibits high blood pressure.",
            status="en_cours"
        )
        url = reverse('consultation_summary', args=[consultation.consultationID])
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['diagnostic'], 'Hypertension')
        self.assertEqual(response.data['patient']['prenom'], 'John')
        self.assertEqual(response.data['patient']['nom'], 'Doe')
        self.assertIn('complementary_exams', response.data)
        self.assertIn('ordonnance', response.data)

    def test_access_patient_not_assigned_to_medecin(self):
        # Create another Médecin and Patient
        another_medecin_user = User.objects.create_user(
            username='medecin2',
            email='medecin2@example.com',
            password='medecinpass2',
            role='medecin',
            centreHospitalier=self.centre
        )
        another_medecin = Medecin.objects.create(
            user=another_medecin_user,
            specialite='chirurgien',
            telephone='0987654321'
        )
        another_patient = Patient.objects.create(
            NSS=987654321098,
            nom='Smith',
            prenom='Jane',
            dateNaissance='1985-05-20',
            adresse='456 Elm St',
            telephone='0123456789',
            email='jane.smith@example.com',
            mutuelle='Mutuelle B',
            contactUrgence='John Smith',
            medecin=another_medecin,
            centreHospitalier=self.centre,
            password='password456',
        )
        another_dossier = DossierMedical.objects.create(
            patient=another_patient,
            qrCode='qr-code-5678',
            active=True,
        )

        url = reverse('search_and_retrieve_dossier')
        response = self.client.get(url, {'query': '987654321098'}, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "You do not have permission to access this patient's dossier.")

    def test_search_patient_without_query(self):
        url = reverse('search_and_retrieve_dossier')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Query parameter is required.')

    def test_search_nonexistent_patient(self):
        url = reverse('search_and_retrieve_dossier')
        response = self.client.get(url, {'query': 'nonexistent'}, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Patient not found.')

    def tearDown(self):
        self.client.credentials(HTTP_AUTHORIZATION='')  # Clear credentials