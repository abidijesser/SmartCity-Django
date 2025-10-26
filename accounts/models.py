from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class UserProfile(models.Model):
    """
    Profile utilisateur étendu avec le lien vers l'ontologie RDF
    """
    ROLE_CHOICES = [
        ('Conducteur', 'Conducteur'),
        ('Passager', 'Passager'),
        ('GestionnaireTransport', 'Gestionnaire'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Passager')
    linked_uri = models.URLField(max_length=500, blank=True, null=True, 
                                  help_text="URI de l'individu dans l'ontologie RDF")
    
    # Informations supplémentaires pour l'ontologie
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
        
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def is_conducteur(self):
        return self.role == 'Conducteur'
    
    def is_passager(self):
        return self.role == 'Passager'
    
    def is_gestionnaire(self):
        return self.role == 'GestionnaireTransport'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil utilisateur lors de la création d'un user"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde automatiquement le profil utilisateur"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
