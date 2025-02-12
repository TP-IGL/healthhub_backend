from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

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
    dateNaissance = models.DateField()
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    mutuelle = models.CharField(max_length=255)
    contactUrgence = models.CharField(max_length=255)
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True)
    createdAt = models.DateField(auto_now_add=True)
    centreHospitalier = models.ForeignKey(CentreHospitalier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

# DossierMedical Model
class DossierMedical(models.Model):
    dossierID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    createdAt = models.DateField(auto_now_add=True)
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
    dateConsultation = models.DateField()
    diagnostic = models.TextField()
    resume = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Consultation {self.consultationID} - {self.status}"

# Ordonnance Model
class Ordonnance(models.Model):
    ordonnanceID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    valide = models.BooleanField(default=False)
    dateCreation = models.DateField(auto_now_add=True)
    dateExpiration = models.DateField(null=True, blank=True)

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
    createdAt = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Activité {self.typeActivite} pour {self.infermier}"



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
    dateAnalyse = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Résultat Labo {self.resLaboID} - {self.status}"

# HealthMetrics Model
class HealthMetrics(models.Model):
    METRIC_TYPE_CHOICES = [
        ('pression_arterielle', 'Pression Artérielle'),
        ('glycemie', 'Glycémie'),
        ('niveaux_cholesterol', 'Niveaux de Cholestérol'),
        ('autre', 'Autre'),
    ]

    id = models.AutoField(primary_key=True)
    medical_record_id = models.IntegerField(default=0)
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    measured_at = models.DateField(auto_now_add=True)
    recorded_by = models.IntegerField(default=0)
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

    # to be updated later , with radiologue_id in ResultatRadio not here , i did null here cz it may be null in case of labo
    radiologue = models.ForeignKey(Radiologue, on_delete=models.CASCADE, null=True, blank=True)
    laborantin = models.ForeignKey(Laboratin, on_delete=models.CASCADE, null=True, blank=True)
    # patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor_details = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    createdAt = models.DateField(auto_now_add=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES)

    def __str__(self):
        return f"Examen {self.type} pour {self.consultation.dossier.patient}"

# Radiologue Model (Already Defined Earlier)

# ResultatRadio Model
class ResultatRadio(models.Model):

    RESRADIO_TYPE_CHOICES = [
        ('radiographie', 'Radiographie'),
        ('echographie', 'Échographie'),
        ('scanner', 'Scanner'),
        ('irm', 'IRM'),
    ]

    resRadioID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # radiologue = models.ForeignKey(Radiologue, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    radioImgURL = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=RESRADIO_TYPE_CHOICES)
    rapport = models.TextField()
    dateRealisation = models.DateField(auto_now_add=True)
    # status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Résultat Radio {self.resRadioID} - {self.examen.etat}"


    
