from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import SignUpForm, LoginForm
from .sparql_utils import sparql, FUSEKI_AVAILABLE

# Create your views here.

def home_view(request):
    """Vue d'accueil qui redirige vers login ou dashboard"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')

def signup_view(request):
    """Vue pour l'inscription des utilisateurs"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Récupérer le profil créé automatiquement
            profile = user.profile
            profile.role = form.cleaned_data['role']
            profile.telephone = form.cleaned_data.get('telephone', '')
            profile.save()
            
            messages.success(request, f'Compte créé avec succès! Vous êtes connecté en tant que {profile.role}.')
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Vue pour la connexion des utilisateurs"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.username}!')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Vue pour la déconnexion des utilisateurs"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """Vue pour le tableau de bord de l'utilisateur selon son rôle"""
    user = request.user
    profile = user.profile
    
    # Contexte de base pour tous les dashboards
    context = {
        'user': user,
        'profile': profile,
        'fuseki_available': FUSEKI_AVAILABLE
    }
    
    # Ajouter des données SPARQL si disponible
    if FUSEKI_AVAILABLE:
        try:
            if profile.is_conducteur():
                context['vehicles'] = sparql.get_vehicles()[:5]
            elif profile.is_passager():
                context['stations'] = sparql.get_all_stations()[:5]
                context['trips'] = sparql.search_trips()[:5]
            elif profile.is_gestionnaire():
                context['stations'] = sparql.get_all_stations()[:10]
                context['vehicles'] = sparql.get_vehicles()[:10]
                context['events'] = sparql.get_traffic_events(limit=5)
        except Exception as e:
            context['sparql_error'] = str(e)
    
    # Redirection selon le rôle
    if profile.is_conducteur():
        return render(request, 'accounts/dashboard_conducteur.html', context)
    elif profile.is_passager():
        return render(request, 'accounts/dashboard_passager.html', context)
    elif profile.is_gestionnaire():
        return render(request, 'accounts/dashboard_gestionnaire.html', context)
    else:
        return render(request, 'accounts/dashboard.html', context)


def profile_view(request):
    """Vue pour afficher et modifier le profil utilisateur"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Mise à jour du profil
        profile.telephone = request.POST.get('telephone', '')
        profile.linked_uri = request.POST.get('linked_uri', '')
        profile.save()
        
        # Mise à jour du User
        if 'email' in request.POST:
            user.email = request.POST.get('email')
        user.save()
        
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile
    })
