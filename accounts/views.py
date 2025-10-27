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


# ============================================
# GESTION CRUD DES TRAJETS (Conducteurs uniquement)
# ============================================

@login_required
def trajets_list_view(request):
    """Liste tous les trajets (réservé aux conducteurs)"""
    # Vérifier que l'utilisateur est conducteur
    if not request.user.profile.is_conducteur():
        messages.error(request, 'Seuls les conducteurs peuvent gérer les trajets.')
        return redirect('accounts:dashboard')
    
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'trajets': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            trajets = sparql.get_all_trajets()
            for t in trajets:
                context['trajets'].append({
                    'uri': t.get('trajet', ''),
                    'depart_nom': t.get('departNom', 'N/A'),
                    'arrivee_nom': t.get('arriveeNom', 'N/A'),
                    'vehicule_nom': t.get('vehiculeNom', 'N/A'),
                    'heure_depart': t.get('heureDepart', 'N/A'),
                    'heure_arrivee': t.get('heureArrivee', 'N/A'),
                    'distance': t.get('distanceTrajet', 'N/A'),
                    'duree': t.get('dureeTrajet', 'N/A')
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/trajets_list.html', context)


@login_required
def trajet_create_view(request):
    """Crée un nouveau trajet (réservé aux conducteurs)"""
    # Vérifier que l'utilisateur est conducteur
    if not request.user.profile.is_conducteur():
        messages.error(request, 'Seuls les conducteurs peuvent créer des trajets.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        depart_station_uri = request.POST.get('depart_station')
        arrivee_station_uri = request.POST.get('arrivee_station')
        vehicule_uri = request.POST.get('vehicule') or None
        heure_depart = request.POST.get('heure_depart') or None
        heure_arrivee = request.POST.get('heure_arrivee') or None
        distance = request.POST.get('distance')
        duree = request.POST.get('duree')
        nom_trajet = request.POST.get('nom_trajet') or None
        
        # Convertir les valeurs numériques
        try:
            distance = float(distance) if distance else None
            duree = float(duree) if duree else None
        except ValueError:
            messages.error(request, 'Distance et durée doivent être des nombres.')
            return redirect('accounts:trajet_create')
        
        # Créer le trajet
        success = sparql.addTrajet(
            depart_station_uri=depart_station_uri,
            arrivee_station_uri=arrivee_station_uri,
            vehicule_uri=vehicule_uri,
            heure_depart=heure_depart,
            heure_arrivee=heure_arrivee,
            distance=distance,
            duree=duree,
            nom_trajet=nom_trajet
        )
        
        if success:
            messages.success(request, 'Trajet créé avec succès!')
            return redirect('accounts:trajets_list')
        else:
            messages.error(request, 'Erreur lors de la création du trajet.')
    
    # Récupérer les stations et véhicules pour le formulaire
    stations = []
    vehicules = []
    
    if FUSEKI_AVAILABLE:
        try:
            stations = sparql.get_all_stations()
            vehicules = sparql.get_vehicles()
        except Exception as e:
            messages.error(request, f'Erreur lors du chargement des données: {str(e)}')
    
    return render(request, 'accounts/trajet_form.html', {
        'stations': stations,
        'vehicules': vehicules,
        'title': 'Créer un Trajet',
        'submit_label': 'Créer',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def trajet_delete_view(request, trajet_uri):
    """Supprime un trajet (réservé aux conducteurs)"""
    from urllib.parse import unquote
    
    # Vérifier que l'utilisateur est conducteur
    if not request.user.profile.is_conducteur():
        messages.error(request, 'Seuls les conducteurs peuvent supprimer des trajets.')
        return redirect('accounts:dashboard')
    
    trajet_uri = unquote(trajet_uri)
    
    if request.method == 'POST':
        success = sparql.delete_trajet(trajet_uri)
        if success:
            messages.success(request, 'Trajet supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression du trajet.')
        return redirect('accounts:trajets_list')
    
    # Récupérer les infos du trajet pour confirmation
    trajets = sparql.get_all_trajets()
    trajet_data = None
    
    for t in trajets:
        if t.get('trajet', '') == trajet_uri:
            trajet_data = {
                'uri': t.get('trajet', ''),
                'depart_nom': t.get('departNom', 'N/A'),
                'arrivee_nom': t.get('arriveeNom', 'N/A'),
                'vehicule_nom': t.get('vehiculeNom', 'N/A'),
                'heure_depart': t.get('heureDepart', 'N/A'),
                'heure_arrivee': t.get('heureArrivee', 'N/A')
            }
            break
    
    if not trajet_data:
        messages.error(request, 'Trajet non trouvé.')
        return redirect('accounts:trajets_list')
    
    return render(request, 'accounts/trajet_confirm_delete.html', {
        'trajet': trajet_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES STATIONS (Gestionnaires uniquement)
# ============================================

@login_required
def stations_list_view(request):
    """Liste toutes les stations (réservé aux gestionnaires)"""
    # Vérifier que l'utilisateur est gestionnaire
    if not request.user.profile.is_gestionnaire():
        messages.error(request, 'Seuls les gestionnaires peuvent gérer les stations.')
        return redirect('accounts:dashboard')
    
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'stations': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            stations = sparql.get_all_stations()
            for s in stations:
                type_uri = s.get('type', '')
                type_name = type_uri.split('#')[-1] if '#' in type_uri else 'Station'
                
                context['stations'].append({
                    'uri': s.get('station', ''),
                    'nom': s.get('nom', 'N/A'),
                    'adresse': s.get('adresse', 'N/A'),
                    'latitude': s.get('latitude', 'N/A'),
                    'longitude': s.get('longitude', 'N/A'),
                    'type': type_name
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/stations_list.html', context)


@login_required
def station_create_view(request):
    """Crée une nouvelle station (réservé aux gestionnaires)"""
    # Vérifier que l'utilisateur est gestionnaire
    if not request.user.profile.is_gestionnaire():
        messages.error(request, 'Seuls les gestionnaires peuvent créer des stations.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        type_station = request.POST.get('type_station')
        adresse = request.POST.get('adresse') or None
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        ville_uri = request.POST.get('ville') or None
        
        # Convertir les valeurs numériques
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            messages.error(request, 'Latitude et longitude doivent être des nombres.')
            return redirect('accounts:station_create')
        
        # Créer la station
        success = sparql.addStation(
            nom=nom,
            type_station=type_station,
            adresse=adresse,
            latitude=latitude,
            longitude=longitude,
            ville_uri=ville_uri
        )
        
        if success:
            messages.success(request, 'Station créée avec succès!')
            return redirect('accounts:stations_list')
        else:
            messages.error(request, 'Erreur lors de la création de la station.')
    
    # Récupérer les villes pour le formulaire
    villes = []
    
    if FUSEKI_AVAILABLE:
        try:
            villes = sparql.get_all_villes()
        except Exception as e:
            messages.error(request, f'Erreur lors du chargement des villes: {str(e)}')
    
    return render(request, 'accounts/station_form.html', {
        'villes': villes,
        'title': 'Créer une Station',
        'submit_label': 'Créer',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def station_delete_view(request, station_uri):
    """Supprime une station (réservé aux gestionnaires)"""
    from urllib.parse import unquote
    
    # Vérifier que l'utilisateur est gestionnaire
    if not request.user.profile.is_gestionnaire():
        messages.error(request, 'Seuls les gestionnaires peuvent supprimer des stations.')
        return redirect('accounts:dashboard')
    
    station_uri = unquote(station_uri)
    
    if request.method == 'POST':
        success = sparql.delete_station(station_uri)
        if success:
            messages.success(request, 'Station supprimée avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression de la station.')
        return redirect('accounts:stations_list')
    
    # Récupérer les infos de la station pour confirmation
    stations = sparql.get_all_stations()
    station_data = None
    
    for s in stations:
        if s.get('station', '') == station_uri:
            type_uri = s.get('type', '')
            type_name = type_uri.split('#')[-1] if '#' in type_uri else 'Station'
            
            station_data = {
                'uri': s.get('station', ''),
                'nom': s.get('nom', 'N/A'),
                'adresse': s.get('adresse', 'N/A'),
                'type': type_name
            }
            break
    
    if not station_data:
        messages.error(request, 'Station non trouvée.')
        return redirect('accounts:stations_list')
    
    return render(request, 'accounts/station_confirm_delete.html', {
        'station': station_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })
