import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from healthhub_back.models import CentreHospitalier, Medecin  # Replace `healthhub_back` with your app name

User = get_user_model()

@pytest.mark.django_db
def test_patient_create_view():
    # Create an admin user and authenticate
    admin_user = User.objects.create_superuser(username="aimen", password="1234", email="admin@example.com", role="admin")
    client = APIClient()
    client.login(username="aimen", password="1234")

    # Create a CentreHospitalier and Medecin for the patient
    centre = CentreHospitalier.objects.create(nom="Centre Test", place="Test City")
    medecin_user = User.objects.create_user(username="medecin", password="1234", email="medecin@example.com", role="medecin")
    medecin = Medecin.objects.create(user=medecin_user, specialite="generaliste", telephone="123456789")

    # Define patient data
    patient_data = {
        "username": "patient1",
        "email": "patient1@example.com",
        "password": "password123",
        "NSS": 123456789,
        "nom": "Doe",
        "prenom": "John",
        "dateNaissance": "1990-01-01",
        "adresse": "123 Test Street",
        "telephone": "123456789",
        "mutuelle": "Mutuelle Test",
        "contactUrgence": "Emergency Contact",
        "medecin": medecin.pk,
        "centreHospitalier": centre.pk,
    }

    # Send POST request to create a patient
    url = reverse("patient-create")
    response = client.post(url, patient_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Patient créé avec succès"
    assert "patient" in response.data
    assert "dossier_id" in response.data


@pytest.mark.django_db
def test_patient_create_duplicate_email():
    # Create an admin user and authenticate
    admin_user = User.objects.create_superuser(username="aimen", password="1234", email="admin@example.com", role="admin")
    client = APIClient()
    client.login(username="aimen", password="1234")

    # Create an existing user with the same email
    User.objects.create_user(username="existing_user", email="duplicate@example.com", password="1234", role="patient")

    # Define patient data with a duplicate email
    patient_data = {
        "username": "new_user",
        "email": "duplicate@example.com",  # Duplicate email
        "password": "password123",
        "NSS": 123456789,
        "nom": "Doe",
        "prenom": "John",
        "dateNaissance": "1990-01-01",
        "adresse": "123 Test Street",
        "telephone": "123456789",
        "mutuelle": "Mutuelle Test",
        "contactUrgence": "Emergency Contact",
        "medecin": None,
        "centreHospitalier": None,
    }

    # Send POST request to create a patient
    url = reverse("patient-create")
    response = client.post(url, patient_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cet email existe déjà." in response.data["email"]


@pytest.mark.django_db
def test_patient_create_invalid_medecin():
    # Create an admin user and authenticate
    admin_user = User.objects.create_superuser(username="aimen", password="1234", email="admin@example.com", role="admin")
    client = APIClient()
    client.login(username="aimen", password="1234")

    # Create a CentreHospitalier
    centre = CentreHospitalier.objects.create(nom="Centre Test", place="Test City")

    # Define patient data with an invalid medecin
    patient_data = {
        "username": "patient2",
        "email": "patient2@example.com",
        "password": "password123",
        "NSS": 987654321,
        "nom": "Smith",
        "prenom": "Jane",
        "dateNaissance": "1995-05-05",
        "adresse": "456 Test Avenue",
        "telephone": "987654321",
        "mutuelle": "Mutuelle Test",
        "contactUrgence": "Emergency Contact",
        "medecin": 9999,  # Invalid medecin ID
        "centreHospitalier": centre.pk,
    }

    # Send POST request to create a patient
    url = reverse("patient-create")
    response = client.post(url, patient_data, format="json")

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
