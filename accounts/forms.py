from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class SignUpForm(UserCreationForm):
    """Formulaire d'inscription avec choix du rôle"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone (optionnel)'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'telephone']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})


class LoginForm(forms.Form):
    """Formulaire de connexion"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )


class VehiculeForm(forms.Form):
    """Formulaire pour créer/modifier un véhicule"""
    
    TYPE_CHOICES = [
        ('Bus', 'Bus'),
        ('Taxi', 'Taxi'),
        ('Véhicule', 'Véhicule'),
    ]
    
    nom = forms.CharField(
        required=True,
        max_length=200,
        label="Nom du véhicule",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: Bus Ligne 1'
        })
    )
    
    type_vehicule = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type de véhicule",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    matricule = forms.CharField(
        required=False,
        max_length=50,
        label="Matricule",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: TN-1234-BUS'
        })
    )
    
    capacite = forms.IntegerField(
        required=False,
        label="Capacité (nombre de passagers)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 50',
            'min': '1'
        })
    )
    
    vitesse_moyenne = forms.FloatField(
        required=False,
        label="Vitesse moyenne (km/h)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 35.5',
            'step': '0.1',
            'min': '0'
        })
    )


class HoraireForm(forms.Form):
    """Formulaire pour créer/modifier un horaire"""
    
    TYPE_CHOICES = [
        ('Horaire', 'Horaire Standard'),
        ('HoraireBus', 'Horaire Bus'),
        ('HoraireTrain', 'Horaire Train'),
        ('HoraireTrafic', 'Horaire Trafic'),
    ]
    
    TYPE_VEHICULE_CHOICES = [
        ('Bus', 'Bus'),
        ('Taxi', 'Taxi'),
        ('Metro', 'Metro'),
    ]
    
    JOUR_CHOICES = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche'),
    ]
    
    type_horaire = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type/Catégorie d'horaire",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    typeVehicule = forms.ChoiceField(
        required=True,
        choices=TYPE_VEHICULE_CHOICES,
        label="Type de véhicule",
        initial='Bus',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    heureDepart = forms.TimeField(
        required=True,
        label="Heure de départ",
        widget=forms.TimeInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'type': 'time',
            'placeholder': '08:00'
        })
    )
    
    heureArrivee = forms.TimeField(
        required=True,
        label="Heure d'arrivée",
        widget=forms.TimeInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'type': 'time',
            'placeholder': '09:30'
        })
    )
    
    jour = forms.ChoiceField(
        required=False,
        choices=[('', '-- Tous les jours --')] + JOUR_CHOICES,
        label="Jour de la semaine",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )


class TrajetForm(forms.Form):
    """Formulaire pour créer un trajet"""
    
    TYPE_TRAJET_CHOICES = [
        ('TrajetCourt', 'Trajet Court'),
        ('TrajetLong', 'Trajet Long'),
        ('TrajetTouristique', 'Trajet Touristique'),
    ]
    
    type_trajet = forms.ChoiceField(
        required=True,
        choices=TYPE_TRAJET_CHOICES,
        label="Type de trajet",
        initial='TrajetCourt',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )


class ParkingForm(forms.Form):
    """Formulaire pour créer/modifier un parking"""
    
    TYPE_CHOICES = [
        ('Parking', 'Parking Standard'),
        ('ParkingPublic', 'Parking Public'),
        ('ParkingPrivé', 'Parking Privé'),
    ]
    
    nom = forms.CharField(
        required=True,
        max_length=200,
        label="Nom du parking",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: Parking Central'
        })
    )
    
    type_parking = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type de parking",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    nombrePlaces = forms.IntegerField(
        required=True,
        label="Nombre de places total",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 100',
            'min': '1'
        })
    )
    
    placesDisponibles = forms.IntegerField(
        required=False,
        label="Places disponibles actuellement",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 45',
            'min': '0'
        })
    )
    
    adresse = forms.CharField(
        required=False,
        max_length=500,
        label="Adresse",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 123 Avenue Habib Bourguiba'
        })
    )
    
    latitude = forms.FloatField(
        required=False,
        label="Latitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 36.8065',
            'step': '0.000001'
        })
    )
    
    longitude = forms.FloatField(
        required=False,
        label="Longitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 10.1815',
            'step': '0.000001'
        })
    )


class EvenementForm(forms.Form):
    """Formulaire pour créer/modifier un événement de trafic"""
    
    TYPE_CHOICES = [
        ('ÉvénementTrafic', 'Événement Standard'),
        ('Accident', 'Accident'),
        ('Travaux', 'Travaux'),
        ('Manifestation', 'Manifestation'),
    ]
    
    type_evt = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type d'événement",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    route = forms.CharField(
        required=False,
        label="Route",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    dateEvenement = forms.DateTimeField(
        required=False,
        label="Date et heure de l'événement",
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'type': 'datetime-local',
            'placeholder': '2025-10-27T14:30'
        })
    )
    
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Description détaillée de l\'événement',
            'rows': 4
        })
    )
    
    latitude = forms.FloatField(
        required=False,
        label="Latitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 36.8065',
            'step': '0.000001'
        })
    )
    
    longitude = forms.FloatField(
        required=False,
        label="Longitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 10.1815',
            'step': '0.000001'
        })
    )


class CapteurForm(forms.Form):
    """Formulaire pour créer/modifier un capteur"""
    
    TYPE_CHOICES = [
        ('CapteurStationnement', 'Capteur de Stationnement'),
        ('CapteurTrafic', 'Capteur de Trafic'),
    ]
    
    ETAT_CHOICES = [
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
        ('En Maintenance', 'En Maintenance'),
    ]
    
    nom = forms.CharField(
        required=True,
        max_length=200,
        label="Nom du capteur",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: Capteur Parking A1'
        })
    )
    
    type_capteur = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type de capteur",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    etat = forms.ChoiceField(
        required=False,
        choices=[('', '-- Sélectionner --')] + ETAT_CHOICES,
        label="État du capteur",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    latitude = forms.FloatField(
        required=False,
        label="Latitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 36.8065',
            'step': '0.000001'
        })
    )
    
    longitude = forms.FloatField(
        required=False,
        label="Longitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 10.1815',
            'step': '0.000001'
        })
    )


class RouteForm(forms.Form):
    """Formulaire pour créer/modifier une route"""
    
    TYPE_CHOICES = [
        ('Autoroute', 'Autoroute'),
        ('RouteRurale', 'Route Rurale'),
        ('RouteUrbaine', 'Route Urbaine'),
    ]
    
    ETAT_CHOICES = [
        ('Bon', 'Bon état'),
        ('Moyen', 'État moyen'),
        ('Mauvais', 'Mauvais état'),
        ('En Travaux', 'En travaux'),
    ]
    
    nom = forms.CharField(
        required=True,
        max_length=200,
        label="Nom de la route",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: A1 Tunis-Sfax'
        })
    )
    
    type_route = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type de route",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    longueur = forms.FloatField(
        required=False,
        label="Longueur (km)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 25.5',
            'step': '0.1',
            'min': '0'
        })
    )
    
    etatRoute = forms.ChoiceField(
        required=False,
        choices=[('', '-- Sélectionner --')] + ETAT_CHOICES,
        label="État de la route",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )


class VilleForm(forms.Form):
    """Formulaire pour créer/modifier une ville"""
    
    TYPE_CHOICES = [
        ('Ville', 'Ville Standard'),
        ('ZoneIndustrielle', 'Zone Industrielle'),
        ('ZoneRésidentielle', 'Zone Résidentielle'),
    ]
    
    nom = forms.CharField(
        required=True,
        max_length=200,
        label="Nom de la ville/zone",
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: Tunis Centre'
        })
    )
    
    type_ville = forms.ChoiceField(
        required=True,
        choices=TYPE_CHOICES,
        label="Type de zone",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
    
    latitude = forms.FloatField(
        required=False,
        label="Latitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 36.8065',
            'step': '0.000001'
        })
    )
    
    longitude = forms.FloatField(
        required=False,
        label="Longitude",
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500',
            'placeholder': 'Ex: 10.1815',
            'step': '0.000001'
        })
    )
