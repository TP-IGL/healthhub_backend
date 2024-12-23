from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Medecin, Infermier, PharmacienHospitalier, Laboratin, Radiologue

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'medecin':
            Medecin.objects.create(user=instance)
        elif instance.role == 'infermier':
            Infermier.objects.create(user=instance)
        elif instance.role == 'pharmacien':
            PharmacienHospitalier.objects.create(user=instance)
        elif instance.role == 'laborantin':
            Laboratin.objects.create(user=instance)
        elif instance.role == 'radiologue':
            Radiologue.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'medecin':
        instance.medecin.save()
    elif instance.role == 'infermier':
        instance.infermier.save()
    elif instance.role == 'pharmacien':
        instance.pharmacienhospitalier.save()
    elif instance.role == 'laborantin':
        instance.laboratin.save()
    elif instance.role == 'radiologue':
        instance.radiologue.save()
        
# To automate the creation of profile instances when a new User is created
# and save the profile instance when the User is saved, we will use signals.