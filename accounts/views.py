from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import SignUpForm, LoginForm, VehiculeForm
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
    
    # Redirection selon le rôle - TOUS utilisent le nouveau template moderne
    return render(request, 'accounts/dashboard_moderne.html', context)


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


# ============================================
# VUES DE TEST POUR L'INTÉGRATION RDF/FUSEKI
# ============================================

@login_required
def test_villes_view(request):
    """Vue de test pour afficher toutes les villes de l'ontologie"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'villes': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            # Requête SPARQL pour récupérer toutes les villes
            query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
            
            SELECT ?ville ?nom ?latitude ?longitude
            WHERE {
                ?ville rdf:type transport:Ville .
                ?ville transport:nom ?nom .
                OPTIONAL { ?ville transport:latitude ?latitude . }
                OPTIONAL { ?ville transport:longitude ?longitude . }
            }
            ORDER BY ?nom
            """
            
            results = sparql.execute_query(query)
            for result in results:
                ville = {
                    'uri': result.get('ville', {}).get('value', ''),
                    'nom': result.get('nom', {}).get('value', 'N/A'),
                    'latitude': result.get('latitude', {}).get('value', 'N/A'),
                    'longitude': result.get('longitude', {}).get('value', 'N/A'),
                }
                context['villes'].append(ville)
                
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/test_villes.html', context)


@login_required
def test_vehicules_view(request):
    """Vue de test pour afficher tous les véhicules de l'ontologie"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'vehicules': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            # Requête SPARQL pour récupérer tous les véhicules
            query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
            
            SELECT ?vehicule ?nom ?type ?matricule ?capacite
            WHERE {
                ?vehicule rdf:type transport:Véhicule .
                ?vehicule transport:nom ?nom .
                ?vehicule rdf:type ?type .
                FILTER (?type != transport:Véhicule)
                OPTIONAL { ?vehicule transport:matricule ?matricule . }
                OPTIONAL { ?vehicule transport:capacite ?capacite . }
            }
            ORDER BY ?nom
            """
            
            results = sparql.execute_query(query)
            for result in results:
                # Extraire le type de véhicule (Bus, Taxi, etc.)
                type_uri = result.get('type', {}).get('value', '')
                type_name = type_uri.split('#')[-1] if '#' in type_uri else 'N/A'
                
                vehicule = {
                    'uri': result.get('vehicule', {}).get('value', ''),
                    'nom': result.get('nom', {}).get('value', 'N/A'),
                    'type': type_name,
                    'matricule': result.get('matricule', {}).get('value', 'N/A'),
                    'capacite': result.get('capacite', {}).get('value', 'N/A'),
                }
                context['vehicules'].append(vehicule)
                
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/test_vehicules.html', context)


@login_required
def test_stations_view(request):
    """Vue de test pour afficher toutes les stations de l'ontologie"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'stations': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            # Requête SPARQL pour récupérer toutes les stations
            query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
            
            SELECT ?station ?nom ?adresse ?latitude ?longitude ?type ?ville
            WHERE {
                ?station rdf:type transport:Station .
                ?station transport:nom ?nom .
                ?station rdf:type ?type .
                FILTER (?type != transport:Station)
                OPTIONAL { ?station transport:adresse ?adresse . }
                OPTIONAL { ?station transport:latitude ?latitude . }
                OPTIONAL { ?station transport:longitude ?longitude . }
                OPTIONAL { ?station transport:situeDans ?villeUri .
                           ?villeUri transport:nom ?ville .
                         }
            }
            ORDER BY ?nom
            """
            
            results = sparql.execute_query(query)
            for result in results:
                type_uri = result.get('type', {}).get('value', '')
                type_name = type_uri.split('#')[-1] if '#' in type_uri else 'N/A'
                
                station = {
                    'uri': result.get('station', {}).get('value', ''),
                    'nom': result.get('nom', {}).get('value', 'N/A'),
                    'adresse': result.get('adresse', {}).get('value', 'N/A'),
                    'latitude': result.get('latitude', {}).get('value', 'N/A'),
                    'longitude': result.get('longitude', {}).get('value', 'N/A'),
                    'type': type_name,
                    'ville': result.get('ville', {}).get('value', 'N/A'),
                }
                context['stations'].append(station)
                
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/test_stations.html', context)


@login_required
def test_home_view(request):
    """Page d'accueil pour les tests RDF"""
    return render(request, 'accounts/test_home.html', {
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES VÉHICULES
# ============================================

@login_required
def vehicules_list_view(request):
    """Liste tous les véhicules"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'vehicules': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            vehicules = sparql.get_vehicles()
            for v in vehicules:
                context['vehicules'].append({
                    'uri': v.get('vehicule', {}),
                    'nom': v.get('nom', {}),
                    'matricule': v.get('matricule', {}),
                    'capacite': v.get('capacite', {}),
                    'vitesse_moyenne': v.get('vitesseMoyenne', {}),
                    'type': v.get('type', {}).split('#')[-1] if v.get('type', {}) else 'N/A'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/vehicules_list.html', context)


@login_required
def vehicule_create_view(request):
    """Crée un nouveau véhicule"""
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            # Créer le véhicule via SPARQL
            success = sparql.create_vehicule(
                nom=form.cleaned_data['nom'],
                type_vehicule=form.cleaned_data['type_vehicule'],
                matricule=form.cleaned_data.get('matricule', ''),
                capacite=form.cleaned_data.get('capacite'),
                vitesse_moyenne=form.cleaned_data.get('vitesse_moyenne')
            )
            
            if success:
                messages.success(request, 'Véhicule créé avec succès!')
                return redirect('accounts:vehicules_list')
            else:
                messages.error(request, 'Erreur lors de la création du véhicule. Vérifiez que Fuseki est disponible.')
    else:
        form = VehiculeForm()
    
    return render(request, 'accounts/vehicule_form.html', {
        'form': form,
        'title': 'Créer un véhicule',
        'submit_label': 'Créer le véhicule',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def vehicule_detail_view(request, vehicule_uri):
    """Détails d'un véhicule"""
    from urllib.parse import unquote
    vehicule_uri = unquote(vehicule_uri)
    
    # Récupérer les véhicules et trouver celui-ci
    vehicules = sparql.get_vehicles()
    vehicule_data = None
    
    for v in vehicules:
        if v.get('vehicule', {}) == vehicule_uri:
            vehicule_data = {
                'uri': v.get('vehicule', {}),
                'nom': v.get('nom', {}),
                'matricule': v.get('matricule', {}),
                'capacite': v.get('capacite', {}),
                'vitesse_moyenne': v.get('vitesseMoyenne', {}),
                'type': v.get('type', {}).split('#')[-1] if v.get('type', {}) else 'N/A'
            }
            break
    
    if not vehicule_data:
        messages.error(request, 'Véhicule non trouvé.')
        return redirect('accounts:vehicules_list')
    
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            # Mettre à jour le véhicule via SPARQL
            success = sparql.update_vehicule(
                vehicule_uri=vehicule_uri,
                nom=form.cleaned_data.get('nom'),
                matricule=form.cleaned_data.get('matricule', ''),
                capacite=form.cleaned_data.get('capacite'),
                vitesse_moyenne=form.cleaned_data.get('vitesse_moyenne')
            )
            
            if success:
                messages.success(request, 'Véhicule mis à jour avec succès!')
                return redirect('accounts:vehicules_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour du véhicule.')
    else:
        # Pré-remplir le formulaire avec les données existantes
        form = VehiculeForm(initial={
            'nom': vehicule_data['nom'],
            'type_vehicule': vehicule_data['type'],
            'matricule': vehicule_data['matricule'],
            'capacite': vehicule_data['capacite'],
            'vitesse_moyenne': vehicule_data['vitesse_moyenne']
        })
    
    return render(request, 'accounts/vehicule_form.html', {
        'form': form,
        'vehicule': vehicule_data,
        'title': f"Modifier {vehicule_data['nom']}",
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def vehicule_delete_view(request, vehicule_uri):
    """Supprime un véhicule"""
    from urllib.parse import unquote
    vehicule_uri = unquote(vehicule_uri)
    
    if request.method == 'POST':
        success = sparql.delete_vehicule(vehicule_uri)
        if success:
            messages.success(request, 'Véhicule supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression du véhicule.')
        return redirect('accounts:vehicules_list')
    
    # Récupérer les infos du véhicule pour confirmation
    vehicules = sparql.get_vehicles()
    vehicule_data = None
    
    for v in vehicules:
        if v.get('vehicule', {}) == vehicule_uri:
            vehicule_data = {
                'uri': v.get('vehicule', {}),
                'nom': v.get('nom', {}),
                'matricule': v.get('matricule', {}),
                'capacite': v.get('capacite', {}),
                'vitesse_moyenne': v.get('vitesseMoyenne', {}),
                'type': v.get('type', {}).split('#')[-1] if v.get('type', {}) else 'N/A'
            }
            break
    
    if not vehicule_data:
        messages.error(request, 'Véhicule non trouvé.')
        return redirect('accounts:vehicules_list')
    
    return render(request, 'accounts/vehicule_confirm_delete.html', {
        'vehicule': vehicule_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })
