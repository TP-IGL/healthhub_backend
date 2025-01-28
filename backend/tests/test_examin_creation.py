import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from healthhub_back.models import (
    CentreHospitalier, Medecin, Consultation, DossierMedical, Patient, Radiologue, Laboratin, Examen
)

User = get_user_model()

@pytest.mark.django_db
def test_examination_create_view():
    # Create a CentreHospitalier
    centre = CentreHospitalier.objects.create(nom="Centre Test", place="Test City")

    # Create a Medecin
    medecin_user = User.objects.create_user(username="medecin", password="1234", email="medecin@example.com", role="medecin", centreHospitalier=centre)
    medecin = Medecin.objects.create(user=medecin_user, specialite="generaliste", telephone="123456789")

    # Authenticate as the Medecin
    client = APIClient()
    client.login(username="medecin", password="1234")

    # Create a Patient
    patient_user = User.objects.create_user(username="patient", password="1234", email="patient@example.com", role="patient", centreHospitalier=centre)
    patient = Patient.objects.create(
        user=patient_user,
        NSS=123456789,
        nom="Doe",
        prenom="John",
        dateNaissance="1990-01-01",
        adresse="123 Test Street",
        telephone="123456789",
        mutuelle="Mutuelle Test",
        contactUrgence="Emergency Contact",
        medecin=medecin,
        centreHospitalier=centre
    )

    # Create a DossierMedical
    dossier = DossierMedical.objects.create(patient=patient)

    # Create a Consultation
    consultation = Consultation.objects.create(
        dossier=dossier,
        dateConsultation="2025-01-01",
        diagnostic="Test Diagnostic",
        resume="Test Resume",
        status="planifie"
    )

    # Create a Radiologue
    radiologue_user = User.objects.create_user(username="radiologue", password="1234", email="radiologue@example.com", role="radiologue", centreHospitalier=centre)
    radiologue = Radiologue.objects.create(user=radiologue_user, specialite="radiographie", shift="jour", telephone="123456789")

    # Define examination data
    examination_data = {
        "type": "radio",
        "priorite": "urgent",
        "doctor_details": "Details about the doctor",
        "radiologue_id": str(radiologue.user.id),
    }

    # Send POST request to create an examination
    url = reverse("examination-create", kwargs={"consultation_id": consultation.consultationID})
    response = client.post(url, examination_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["type"] == "radio"
    assert response.data["priorite"] == "urgent"
    assert response.data["doctor_details"] == "Details about the doctor"


@pytest.mark.django_db
def test_examination_create_missing_radiologue_id():
    # Create a CentreHospitalier
    centre = CentreHospitalier.objects.create(nom="Centre Test", place="Test City")

    # Create a Medecin
    medecin_user = User.objects.create_user(username="medecin", password="1234", email="medecin@example.com", role="medecin", centreHospitalier=centre)
    medecin = Medecin.objects.create(user=medecin_user, specialite="generaliste", telephone="123456789")

    # Authenticate as the Medecin
    client = APIClient()
    client.login(username="medecin", password="1234")

    # Create a Patient
    patient_user = User.objects.create_user(username="patient", password="1234", email="patient@example.com", role="patient", centreHospitalier=centre)
    patient = Patient.objects.create(
        user=patient_user,
        NSS=123456789,
        nom="Doe",
        prenom="John",
        dateNaissance="1990-01-01",
        adresse="123 Test Street",
        telephone="123456789",
        mutuelle="Mutuelle Test",
        contactUrgence="Emergency Contact",
        medecin=medecin,
        centreHospitalier=centre
    )

    # Create a DossierMedical
    dossier = DossierMedical.objects.create(patient=patient)

    # Create a Consultation
    consultation = Consultation.objects.create(
        dossier=dossier,
        dateConsultation="2025-01-01",
        diagnostic="Test Diagnostic",
        resume="Test Resume",
        status="planifie"
    )

    # Define examination data without radiologue_id
    examination_data = {
        "type": "radio",
        "priorite": "urgent",
        "doctor_details": "Details about the doctor",
    }

    # Send POST request to create an examination
    url = reverse("examination-create", kwargs={"consultation_id": consultation.consultationID})
    response = client.post(url, examination_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "radiologue_id is required for radio examinations" in response.data["non_field_errors"]


@pytest.mark.django_db
def test_examination_create_invalid_laborantin_id():
    # Create a CentreHospitalier
    centre = CentreHospitalier.objects.create(nom="Centre Test", place="Test City")

    # Create a Medecin
    medecin_user = User.objects.create_user(username="medecin", password="1234", email="medecin@example.com", role="medecin", centreHospitalier=centre)
    medecin = Medecin.objects.create(user=medecin_user, specialite="generaliste", telephone="123456789")

    # Authenticate as the Medecin
    client = APIClient()
    client.login(username="medecin", password="1234")

    # Create a Patient
    patient_user = User.objects.create_user(username="patient", password="1234", email="patient@example.com", role="patient", centreHospitalier=centre)
    patient = Patient.objects.create(
        user=patient_user,
        NSS=123456789,
        nom="Doe",
        prenom="John",
        dateNaissance="1990-01-01",
        adresse="123 Test Street",
        telephone="123456789",
        mutuelle="Mutuelle Test",
        contactUrgence="Emergency Contact",
        medecin=medecin,
        centreHospitalier=centre
    )

    # Create a DossierMedical
    dossier = DossierMedical.objects.create(patient=patient)

    # Create a Consultation
    consultation = Consultation.objects.create(
        dossier=dossier,
        dateConsultation="2025-01-01",
        diagnostic="Test Diagnostic",
        resume="Test Resume",
        status="planifie"
    )

    # Define examination data with an invalid laborantin_id
    examination_data = {
        "type": "labo",
        "priorite": "normal",
        "doctor_details": "Details about the doctor",
        "laborantin_id": "invalid-id",  # Invalid laborantin_id
    }

    # Send POST request to create an examination
    url = reverse("examination-create", kwargs={"consultation_id": consultation.consultationID})
    response = client.post(url, examination_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
