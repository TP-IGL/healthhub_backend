# populate_db.py

import os
import django
import uuid
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from healthhub_back.models import * 

def create_sample_data():
    # Clear existing data
    print("Clearing existing data...")
    models_to_clear = [
        Facture, HealthMetrics, ResultatLabo, ResultatRadio, ActiviteInfermier,
        OrdonnanceMedicament, Ordonnance, Consultation, Examen,
        DossierMedical, Medicament,
        Infermier, Laboratin, PharmacienHospitalier, Radiologue,
        Medecin, Patient, User, CentreHospitalier
    ]

    for model in models_to_clear:
        model.objects.all().delete()
        print(f"Deleted all records from {model.__name__}")

    print("Starting database initialization...")

    # Create a single Centre Hospitalier
    print("Creating Centre Hospitalier...")
    centre, created = CentreHospitalier.objects.get_or_create(
        nom="Hôpital Central",
        defaults={"place": "Paris"}
    )
    if created:
        print(f"Created CentreHospitalier: {centre.nom}")
    else:
        print(f"CentreHospitalier already exists: {centre.nom}")

    # Create Users and Profiles
    print("Creating Users and Profiles...")

    # Create Médecins
    medecins = []
    specialites = ['generaliste', 'cardiologue', 'chirurgien']
    for i, spec in enumerate(specialites):
        username = f"medecin{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password":make_password(f"password{i+1}"),
                "email": f"medecin{i+1}@hospital.com",
                "first_name": f"Doctor{i+1}",
                "last_name": f"Smith{i+1}",
                "role": "medecin",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with ID: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        medecin, med_created = Medecin.objects.get_or_create(
            user=user,
            defaults={
                "specialite": spec,
                "telephone": f"+331234567{i:02d}"
            }
        )
        if med_created:
            print(f"Created Medecin profile for: {user.username}")
        else:
            print(f"Medecin profile already exists for: {user.username}")
        medecins.append(medecin)
    # Create Infermiers
    infermiers = []
    shifts = ['jour', 'nuit', 'rotation']
    specialites_inf = ['generale', 'chirurgie', 'pediatrie']
    for i in range(3):
        username = f"infermier{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": make_password(f"password{i+1}"),
                "email": f"infermier{i+1}@hospital.com",
                "first_name": f"Nurse{i+1}",
                "last_name": f"Jones{i+1}",
                "role": "infermier",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with password: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        infermier, inf_created = Infermier.objects.get_or_create(
            user=user,
            defaults={
                "shift": shifts[i % len(shifts)],
                "specialite": specialites_inf[i % len(specialites_inf)],
                "telephone": f"+331234568{i:02d}"
            }
        )
        if inf_created:
            print(f"Created Infermier profile for: {user.username}")
        else:
            print(f"Infermier profile already exists for: {user.username}")
        infermiers.append(infermier)

    # Create Pharmaciens
    pharmaciens = []
    for i in range(2):
        username = f"pharmacien{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": make_password(f"password{i+1}"),
                "email": f"pharmacien{i+1}@hospital.com",
                "first_name": f"Pharm{i+1}",
                "last_name": f"White{i+1}",
                "role": "pharmacien",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with ID: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        pharmacien, pharm_created = PharmacienHospitalier.objects.get_or_create(
            user=user,
            defaults={
                "shift": shifts[i % len(shifts)],
                "telephone": f"+331234569{i:02d}"
            }
        )
        if pharm_created:
            print(f"Created PharmacienHospitalier profile for: {user.username}")
        else:
            print(f"PharmacienHospitalier profile already exists for: {user.username}")
        pharmaciens.append(pharmacien)

    # Create Laborantins
    laborantins = []
    specialites_lab = ['biochimie', 'hematologie', 'microbiologie']
    for i in range(3):
        username = f"laborantin{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": make_password(f"password{i+1}"),
                "email": f"laborantin{i+1}@hospital.com",
                "first_name": f"Lab{i+1}",
                "last_name": f"Brown{i+1}",
                "role": "laborantin",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with ID: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        laborantin, lab_created = Laboratin.objects.get_or_create(
            user=user,
            defaults={
                "shift": shifts[i % len(shifts)],
                "specialite": specialites_lab[i % len(specialites_lab)],
                "telephone": f"+331234570{i:02d}",
                "nombreTests": i * 10
            }
        )
        if lab_created:
            print(f"Created Laboratin profile for: {user.username}")
        else:
            print(f"Laboratin profile already exists for: {user.username}")
        laborantins.append(laborantin)

    # Create Radiologues
    radiologues = []
    specialites_rad = ['radiographie', 'echographie', 'scanner', 'irm']
    for i in range(4):  # Adjusted loop to match the number of specialties
        username = f"radiologue{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": make_password(f"password{i+1}"),
                "email": f"radiologue{i+1}@hospital.com",
                "first_name": f"Rad{i+1}",
                "last_name": f"Black{i+1}",
                "role": "radiologue",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with ID: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        radiologue, rad_created = Radiologue.objects.get_or_create(
            user=user,
            defaults={
                "shift": shifts[i % len(shifts)],
                "specialite": specialites_rad[i % len(specialites_rad)],
                "telephone": f"+331234571{i:02d}",
                "nombreTests": i * 15
            }
        )
        if rad_created:
            print(f"Created Radiologue profile for: {user.username}")
        else:
            print(f"Radiologue profile already exists for: {user.username}")
        radiologues.append(radiologue)

    # Create Patients
    print("Creating Patients...")
    patients = []
    for i in range(5):
        username = f"patient{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": make_password(f"password{i+1}"),
                "email": f"patient{i+1}@example.com",
                "first_name": f"Patient{i+1}",
                "last_name": f"Doe{i+1}",
                "role": "patient",
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if created:
            print(f"Created User: {user.username} with ID: {user.id}")
        else:
            print(f"User already exists: {user.username} with ID: {user.id}")

        patient, pat_created = Patient.objects.get_or_create(
            user=user,
            defaults={
                "NSS": 1234567890 + i,
                "nom": f"Doe{i+1}",
                "prenom": f"Patient{i+1}",
                "dateNaissance": timezone.now() - timedelta(days=365*30 + i*100),
                "adresse": f"{i+1} Rue de Paris",
                "telephone": f"+331234572{i:02d}",
                "mutuelle": "Mutuelle Générale",
                "contactUrgence": f"+331234573{i:02d}",
                "medecin": medecins[i % len(medecins)],
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if pat_created:
            print(f"Created Patient profile for: {user.username}")
        else:
            print(f"Patient profile already exists for: {user.username}")
        patients.append(patient)

    # Create Dossiers Medicaux
    print("Creating Dossiers Medicaux...")
    dossiers = []
    for patient in patients:
        dossier, dos_created = DossierMedical.objects.get_or_create(
            dossierID=uuid.uuid4(),
            defaults={
                "patient": patient,
                "active": True,
                "qrCode": f"QR_{uuid.uuid4().hex[:8]}"
            }
        )
        if dos_created:
            print(f"Created DossierMedical for: {patient}")
        else:
            print(f"DossierMedical already exists for: {patient}")
        dossiers.append(dossier)

    # Create Consultations
    print("Creating Consultations...")
    consultations = []
    status_choices = ['planifie', 'en_cours', 'termine', 'annule']
    for i, dossier in enumerate(dossiers):
        consultation, con_created = Consultation.objects.get_or_create(
            consultationID=uuid.uuid4(),
            defaults={
                "dossier": dossier,
                "dateConsultation": timezone.now() + timedelta(days=i),
                "diagnostic": f"Diagnostic {i+1}",
                "resume": f"Résumé de la consultation {i+1}",
                "status": status_choices[i % len(status_choices)]
            }
        )
        if con_created:
            print(f"Created Consultation {consultation.consultationID} for DossierMedical {dossier}")
        else:
            print(f"Consultation already exists for DossierMedical {dossier}")
        consultations.append(consultation)

    # Create Medicaments
    print("Creating Medicaments...")
    medicaments = []
    types = ['comprime', 'sirop', 'injection', 'pommade']
    for i in range(5):
        medicament, med_created = Medicament.objects.get_or_create(
            medicamentID=uuid.uuid4(),
            defaults={
                "nom": f"Medicament{i+1}",
                "type": types[i % len(types)],
                "description": f"Description du médicament {i+1}"
            }
        )
        if med_created:
            print(f"Created Medicament: {medicament.nom}")
        else:
            print(f"Medicament already exists: {medicament.nom}")
        medicaments.append(medicament)

    # Create Ordonnances and OrdonnanceMedicaments
    print("Creating Ordonnances and OrdonnanceMedicaments...")
    for i, consultation in enumerate(consultations):
        ordonnance, ord_created = Ordonnance.objects.get_or_create(
            ordonnanceID=uuid.uuid4(),
            defaults={
                "consultation": consultation,
                "valide": True,
                "dateExpiration": timezone.now() + timedelta(days=30)
            }
        )
        if ord_created:
            print(f"Created Ordonnance {ordonnance.ordonnanceID} for Consultation {consultation.consultationID}")
        else:
            print(f"Ordonnance already exists for Consultation {consultation.consultationID}")

        for j in range(2):
            ordonnance_medicament, om_created = OrdonnanceMedicament.objects.get_or_create(
                ordonnanceMedicamentID=uuid.uuid4(),
                defaults={
                    "med": medicaments[(i+j) % len(medicaments)],
                    "ordonnance": ordonnance,
                    "duree": f"{j+1} semaines",
                    "dosage": 'moyen',
                    "frequence": "2 fois par jour",
                    "instructions": f"Instructions pour médicament {j+1}"
                }
            )
            if om_created:
                print(f"Created OrdonnanceMedicament for Medicament {ordonnance_medicament.med.nom} in Ordonnance {ordonnance}")
            else:
                print(f"OrdonnanceMedicament already exists for Medicament {ordonnance_medicament.med.nom} in Ordonnance {ordonnance}")

    # Create Examens and Results
    print("Creating Examens and Results...")
    for i, consultation in enumerate(consultations):
        examen_type = 'radio' if i % 2 == 0 else 'labo'
        examen, ex_created = Examen.objects.get_or_create(
            examenID=uuid.uuid4(),
            defaults={
                "consultation": consultation,
                "radiologue": radiologues[i % len(radiologues)] if examen_type == 'radio' else None,
                "doctor_details": f"Details from doctor {i+1}",
                "type": examen_type,
                "etat": 'planifie',
                "priorite": 'normal'
            }
        )
        if ex_created:
            print(f"Created Examen {examen.examenID} of type {examen.type} for Consultation {consultation.consultationID}")
        else:
            print(f"Examen already exists for Consultation {consultation.consultationID}")

        if examen.type == 'labo':
            resultat_labo, lab_created = ResultatLabo.objects.get_or_create(
                resLaboID=uuid.uuid4(),
                defaults={
                    "examen": examen,
                    "laboratin": laborantins[i % len(laborantins)],
                    "resultat": f"Résultats d'analyse {i+1}",
                    "dateAnalyse": timezone.now(),
                    "status": 'termine'
                }
            )
            if lab_created:
                print(f"Created ResultatLabo {resultat_labo.resLaboID} for Examen {examen.examenID}")
                # **Creating HealthMetrics for each ResultatLabo**
                print(f"Creating HealthMetrics for ResultatLabo {resultat_labo.resLaboID}...")
                metric_types = ['pression_arterielle', 'glycemie', 'niveaux_cholesterol']
                for mt in metric_types:
                    # Determine unit based on metric_type
                    if mt == 'pression_arterielle':
                        unit = 'mmHg'
                        value = round(120 + i * 5 + 0.5, 2)  # Example value
                    elif mt == 'glycemie':
                        unit = 'mg/dL'
                        value = round(100 + i * 3 + 0.2, 2)  # Example value
                    elif mt == 'niveaux_cholesterol':
                        unit = 'mg/dL'
                        value = round(200 + i * 4 + 0.3, 2)  # Example value
                    else:
                        unit = 'unités'
                        value = 0.0

                    health_metric, hm_created = HealthMetrics.objects.get_or_create(
                        resLabo=resultat_labo,
                        metric_type=mt,
                        defaults={
                            "medical_record_id": 0,
                            "value": value,
                            "unit": unit,
                            "recorded_by": 0
                        }
                    )
                    if hm_created:
                        print(f"  Created HealthMetric '{health_metric.metric_type}' with value {health_metric.value} {health_metric.unit}")
                    else:
                        print(f"  HealthMetric '{health_metric.metric_type}' already exists for ResultatLabo {resultat_labo.resLaboID}")
            else:
                print(f"ResultatLabo already exists for Examen {examen.examenID}")
        else:
            resultat_radio, rad_created = ResultatRadio.objects.get_or_create(
                resRadioID=uuid.uuid4(),
                defaults={
                    "examen": examen,
                    "radioImgURL": f"https://example.com/radio{i+1}.jpg",
                    "type": 'radiographie',  # Ensure type matches RESRADIO_TYPE_CHOICES
                    "rapport": f"Rapport radiologique {i+1}"
                    # 'status' field removed as it doesn't exist in models.py
                }
            )
            if rad_created:
                print(f"Created ResultatRadio {resultat_radio.resRadioID} for Examen {examen.examenID}")
            else:
                print(f"ResultatRadio already exists for Examen {examen.examenID}")

    # Create ActiviteInfermier
    print("Creating ActiviteInfermier...")
    for i, consultation in enumerate(consultations):
        activite, act_created = ActiviteInfermier.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                "consultation": consultation,
                "infermier": infermiers[i % len(infermiers)],
                "typeActivite": 'administration_medicament',
                "doctors_details": f"Doctor's instructions {i+1}",
                "nurse_observations": f"Nurse observations {i+1}",
                "status": 'planifie'
            }
        )
        if act_created:
            print(f"Created ActiviteInfermier {activite.id} for Consultation {consultation.consultationID}")
        else:
            print(f"ActiviteInfermier already exists for Consultation {consultation.consultationID}")

    # Create Factures
    print("Creating Factures...")
    for i, patient in enumerate(patients):
        facture, fact_created = Facture.objects.get_or_create(
            factureID=uuid.uuid4(),
            defaults={
                "patient": patient,
                "montant": 100.0 * (i + 1),
                "description": f"Facture consultation {i + 1}",
                "datePaiement": timezone.now() if i % 2 == 0 else None,
                "status": 'paye' if i % 2 == 0 else 'en_attente',
                "methodePaiement": 'carte',
                "centreHospitalier": centre  # Assigning to the single hospital
            }
        )
        if fact_created:
            print(f"Created Facture {facture.factureID} for Patient {patient}")
        else:
            print(f"Facture already exists for Patient {patient}")

    print("Database initialization completed successfully!")

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"An error occurred: {str(e)}")