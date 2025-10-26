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

