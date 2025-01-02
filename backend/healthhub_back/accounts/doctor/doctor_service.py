from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from healthhub_back.models import (
    Patient,
    DossierMedical,
    Consultation,
    Ordonnance,
    Medicament,
    OrdonnanceMedicament,
    Examen,
)
from django.db import transaction


def search_patient(query):
    """
    Searches for a patient by NSS or QR code.
    """
    try:
        # Attempt to interpret query as NSS
        nss = int(query)
        patient = get_object_or_404(Patient, NSS=nss)
    except ValueError:
        try:
            # Try to find by User UUID
            patient = get_object_or_404(Patient, user__id=query)
        except ValidationError:
            # If not UUID, treat as QR code
            dossier = get_object_or_404(DossierMedical, qrCode=query)
            patient = dossier.patient
    return patient
# 

def visualize_medical_record(patient):
    """
    Retrieves the patient's medical dossier.

    Parameters:
    - patient (Patient): Patient instance.

    Returns:
    - DossierMedical instance.

    Raises:
    - ValidationError if dossier is not found.
    """
    dossier = get_object_or_404(DossierMedical, patient=patient)
    return dossier


@transaction.atomic
def create_consultation(medecin, patient, data):
    """
    Creates a new consultation. Depending on the presence of a diagnosis,
    it may create an ordonnance or prescribe complementary exams.

    Parameters:
    - medecin (Medecin): Médecin instance.
    - patient (Patient): Patient instance.
    - data (dict): Consultation data containing diagnostics, ordonnance, etc.

    Returns:
    - Consultation instance.

    Raises:
    - ValidationError for any invalid operations.
    """
    # Create Consultation
    consultation = Consultation.objects.create(
        dossier=DossierMedical.objects.get(patient=patient),
        dateConsultation=data.get('dateConsultation'),
        diagnostic=data.get('diagnostic', ''),
        resume=data.get('resume', ''),
        status='en_cours'  # Initial status
    )

    # If diagnostic is provided, create Ordonnance
    if data.get('diagnostic'):
        ordonnance_data = data.get('ordonnance', {})
        date_expiration = ordonnance_data.get('dateExpiration')
        medicaments = ordonnance_data.get('medicaments', [])

        if not date_expiration:
            raise ValidationError("Date d'expiration de l'ordonnance est requise.")

        ordonnance = Ordonnance.objects.create(
            consultation=consultation,
            valide=True,
            dateExpiration=date_expiration
        )

        for med in medicaments:
            medicament_id = med.get('medicament_id')
            duree = med.get('duree')
            dosage = med.get('dosage')
            frequence = med.get('frequence')
            instructions = med.get('instructions', '')

            if not all([medicament_id, duree, dosage, frequence]):
                raise ValidationError("Tous les champs des médicaments sont requis.")

            medicament = get_object_or_404(Medicament, medicamentID=medicament_id)

            OrdonnanceMedicament.objects.create(
                ordonnance=ordonnance,
                med=medicament,
                duree=duree,
                dosage=dosage,
                frequence=frequence,
                instructions=instructions
            )

    else:
        # Prescribe Complementary Exams
        exams = data.get('complementary_exams', {})
        bilan_biologique = exams.get('bilan_biologique', [])
        bilan_radiologique = exams.get('bilan_radiologique', [])

        # Prescribe Bilan Biologique
        for exam in bilan_biologique:
            Examen.objects.create(
                consultation=consultation,
                patient=patient,
                type='labo',
                notes=exam.get('notes', ''),
                etat='planifie',
                priorite=exam.get('priorite', 'normal')
            )

        # Prescribe Bilan Radiologique
        for exam in bilan_radiologique:
            Examen.objects.create(
                consultation=consultation,
                patient=patient,
                type='radio',
                notes=exam.get('notes', ''),
                etat='planifie',
                priorite=exam.get('priorite', 'normal')
            )

    # Update Consultation Status to 'Terminé'
    consultation.status = 'termine'
    consultation.save()

    return consultation