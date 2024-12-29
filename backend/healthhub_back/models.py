# healthhub_backend/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Centre Hospitalier Model
class CentreHospitalier(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    place = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

# Custom User Model
class User(AbstractUser):
    USER_ROLES = [
        ('medecin', 'Médecin'),
        ('infermier', 'Infirmier'),
        ('pharmacien', 'Pharmacien Hospitalier'),
        ('laborantin', 'Laborantin'),
        ('radiologue', 'Radiologue'),
        ('admin', 'Administrateur'),
        ('patient', 'Patient'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    centreHospitalier = models.ForeignKey(CentreHospitalier, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_role_display()} - {self.username}"

# Medecin Profile Model
class Medecin(models.Model):
    SPECIALITE_CHOICES = [
        ('generaliste', 'Généraliste'),
        ('cardiologue', 'Cardiologue'),
        ('chirurgien', 'Chirurgien'),
        ('autre', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialite = models.CharField(max_length=20, choices=SPECIALITE_CHOICES)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

# Infermier Profile Model
class Infermier(models.Model):
    SHIFT_CHOICES = [
        ('jour', 'Jour'),
        ('nuit', 'Nuit'),
        ('rotation', 'Rotation'),
    ]

    SPECIALITE_CHOICES = [
        ('generale', 'Générale'),
        ('chirurgie', 'Chirurgie'),
        ('pediatrie', 'Pédiatrie'),
        ('autre', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    specialite = models.CharField(max_length=20, choices=SPECIALITE_CHOICES)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return f"Infirmier {self.user.first_name} {self.user.last_name}"

# PharmacienHospitalier Profile Model
class PharmacienHospitalier(models.Model):
    SHIFT_CHOICES = [
        ('jour', 'Jour'),
        ('nuit', 'Nuit'),
        ('rotation', 'Rotation'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    telephone = models.CharField(max_length=20)
    # Add any additional fields specific to PharmacienHospitalier

    def __str__(self):
        return f"Pharmacien {self.user.first_name} {self.user.last_name}"

# Laborantin Profile Model
class Laboratin(models.Model):
    SHIFT_CHOICES = [
        ('jour', 'Jour'),
        ('nuit', 'Nuit'),
        ('rotation', 'Rotation'),
    ]

    SPECIALITE_CHOICES = [
        ('biochimie', 'Biochimie'),
        ('hematologie', 'Hématologie'),
        ('microbiologie', 'Microbiologie'),
        ('autre', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    specialite = models.CharField(max_length=20, choices=SPECIALITE_CHOICES)
    telephone = models.CharField(max_length=20)
    nombreTests = models.IntegerField(default=0)

    def __str__(self):
        return f"Laborantin {self.user.first_name} {self.user.last_name}"

# Radiologue Profile Model
class Radiologue(models.Model):
    SHIFT_CHOICES = [
        ('jour', 'Jour'),
        ('nuit', 'Nuit'),
        ('rotation', 'Rotation'),
    ]

    SPECIALITE_CHOICES = [
        ('radiographie', 'Radiographie'),
        ('echographie', 'Échographie'),
        ('scanner', 'Scanner'),
        ('irm', 'IRM'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    specialite = models.CharField(max_length=20, choices=SPECIALITE_CHOICES)
    telephone = models.CharField(max_length=20)
    nombreTests = models.IntegerField(default=0)

    def __str__(self):
        return f"Radiologue {self.user.first_name} {self.user.last_name}"

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    NSS = models.BigIntegerField(unique=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    dateNaissance = models.DateTimeField()
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    mutuelle = models.CharField(max_length=255)
    contactUrgence = models.CharField(max_length=255)
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    centreHospitalier = models.ForeignKey(CentreHospitalier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# DossierMedical Model
class DossierMedical(models.Model):
    dossierID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    qrCode = models.CharField(max_length=10000)

    def __str__(self):
        return f"Dossier de {self.patient}"
# Consultation Model
class Consultation(models.Model):
    STATUS_CHOICES = [
        ('planifie', 'Planifiée'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminée'),
        ('annule', 'Annulée'),
    ]

    consultationID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE)
    dateConsultation = models.DateTimeField()
    diagnostic = models.TextField()
    resume = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Consultation {self.consultationID} - {self.status}"

# Ordonnance Model
class Ordonnance(models.Model):
    ordonnanceID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    valide = models.BooleanField(default=True)
    dateCreation = models.DateTimeField(auto_now_add=True)
    dateExpiration = models.DateTimeField()

    def __str__(self):
        return f"Ordonnance {self.ordonnanceID}"

# Medicament Model
class Medicament(models.Model):
    TYPE_CHOICES = [
        ('comprime', 'Comprimé'),
        ('sirop', 'Sirop'),
        ('injection', 'Injection'),
        ('pommade', 'Pommade'),
        ('autre', 'Autre'),
    ]

    medicamentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()

    class Meta:
        unique_together = ('nom', 'type')

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

# OrdonnanceMedicament Model
class OrdonnanceMedicament(models.Model):
    DOSAGE_CHOICES = [
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('fort', 'Fort'),
    ]

    ordonnanceMedicamentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    med = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE)
    duree = models.CharField(max_length=50)
    dosage = models.CharField(max_length=10, choices=DOSAGE_CHOICES)
    frequence = models.CharField(max_length=50)
    instructions = models.TextField()

    def __str__(self):
        return f"Médicament {self.med.nom} pour {self.ordonnance}"

# Infermier Model (Already Defined Earlier)

# ActiviteInfermier Model
class ActiviteInfermier(models.Model):
    TYPE_ACTIVITE_CHOICES = [
        ('administration_medicament', 'Administration de Médicament'),
        ('soins', 'Soins'),
        ('observation', 'Observation'),
        ('prelevement', 'Prélèvement'),
        ('autre', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('planifie', 'Planifiée'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    infermier = models.ForeignKey(Infermier, on_delete=models.CASCADE)
    typeActivite = models.CharField(max_length=50, choices=TYPE_ACTIVITE_CHOICES)
    doctors_details = models.TextField()
    nurse_observations = models.TextField()
    # details = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Activité {self.typeActivite} pour {self.infermier}"

# NurseMedication Model
# class NurseMedication(models.Model):
#     STATUS_CHOICES = [
#         ('planifie', 'Planifiée'),
#         ('administre', 'Administrée'),
#         ('reporte', 'Reportée'),
#         ('annule', 'Annulée'),
#     ]

#     DOSAGE_CHOICES = [
#         ('faible', 'Faible'),
#         ('moyen', 'Moyen'),
#         ('fort', 'Fort'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     nurseActivite = models.ForeignKey(ActiviteInfermier, on_delete=models.CASCADE)
#     ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE)
#     administeredAt = models.DateTimeField(null=True, blank=True)
#     # dosage = models.CharField(max_length=10, choices=DOSAGE_CHOICES)
#     notes = models.TextField(blank=True, null=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     def __str__(self):
#         return f"Médicament {self.ordonnance} administré par {self.nurseActivite.infermier}"


# ResultatLabo Model
class ResultatLabo(models.Model):
    STATUS_CHOICES = [
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('valide', 'Validé'),
    ]

    resLaboID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    examen = models.ForeignKey('Examen', on_delete=models.CASCADE)
    laboratin = models.ForeignKey(Laboratin, on_delete=models.CASCADE)
    resultat = models.TextField()
    dateAnalyse = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Résultat Labo {self.resLaboID} - {self.status}"

# HealthMetrics Model
class HealthMetrics(models.Model):
    METRIC_TYPE_CHOICES = [
        ('temperature', 'Température'),
        ('pression_arterielle', 'Pression Artérielle'),
        ('glycemie', 'Glycémie'),
        ('autre', 'Autre'),
    ]

    id = models.AutoField(primary_key=True)
    medical_record_id = models.IntegerField()
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    measured_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.IntegerField()
    resLabo = models.ForeignKey(ResultatLabo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.metric_type} - {self.value} {self.unit}"

# Examen Model
class Examen(models.Model):
    TYPE_CHOICES = [
        ('labo', 'Laboratoire'),
        ('radio', 'Radiologie'),
    ]

    ETAT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    PRIORITE_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('tres_urgent', 'Très Urgent'),
    ]

    examenID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    radiologue = models.ForeignKey(Radiologue, on_delete=models.CASCADE)
    # patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor_details = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    createdAt = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES)

    def __str__(self):
        return f"Examen {self.type} pour {self.patient}"

# Radiologue Model (Already Defined Earlier)

# ResultatRadio Model
class ResultatRadio(models.Model):
    # STATUS_CHOICES = [
    #     ('en_cours', 'En Cours'),
    #     ('termine', 'Terminé'),
    #     ('valide', 'Validé'),
    # ]

    RESRADIO_TYPE_CHOICES = [
        ('radiographie', 'Radiographie'),
        ('echographie', 'Échographie'),
        ('scanner', 'Scanner'),
        ('irm', 'IRM'),
    ]

    resRadioID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # radiologue = models.ForeignKey(Radiologue, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    radioImgURL = models.URLField(max_length=500, blank=True, null=True)
    type = models.CharField(max_length=20, choices=RESRADIO_TYPE_CHOICES)
    rapport = models.TextField()
    dateRealisation = models.DateTimeField(auto_now_add=True)
    # status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Résultat Radio {self.resRadioID} - {self.status}"

# Facture Model
class Facture(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En Attente'),
        ('paye', 'Payée'),
        ('annule', 'Annulée'),
    ]

    METHOD_PAIEMENT_CHOICES = [
        ('carte', 'Carte'),
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('autre', 'Autre'),
    ]

    factureID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    montant = models.FloatField()
    description = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    datePaiement = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    methodePaiement = models.CharField(max_length=20, choices=METHOD_PAIEMENT_CHOICES)
    centreHospitalier = models.ForeignKey(CentreHospitalier, on_delete=models.CASCADE)

    def __str__(self):
        return f"Facture {self.factureID} - {self.status}"