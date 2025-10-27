from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import SignUpForm, LoginForm, VehiculeForm, HoraireForm, ParkingForm, EvenementForm, CapteurForm, RouteForm, VilleForm
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


# ============================================
# GESTION CRUD DES HORAIRES
# ============================================

@login_required
def horaires_list_view(request):
    """Liste tous les horaires"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'horaires': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            horaires = sparql.get_horaires()
            for h in horaires:
                context['horaires'].append({
                    'uri': h.get('horaire', ''),
                    'heureDepart': h.get('heureDepart', 'N/A'),
                    'heureArrivee': h.get('heureArrivee', 'N/A'),
                    'jour': h.get('jour', 'Tous les jours'),
                    'type': h.get('type', '').split('#')[-1] if h.get('type', '') else 'Horaire'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/horaires_list.html', context)


@login_required
def horaire_create_view(request):
    """Crée un nouvel horaire"""
    if request.method == 'POST':
        form = HoraireForm(request.POST)
        if form.is_valid():
            success = sparql.create_horaire(
                heureDepart=str(form.cleaned_data['heureDepart']),
                heureArrivee=str(form.cleaned_data['heureArrivee']),
                jour=form.cleaned_data.get('jour') or None,
                type_horaire=form.cleaned_data['type_horaire']
            )
            
            if success:
                messages.success(request, 'Horaire créé avec succès!')
                return redirect('accounts:horaires_list')
            else:
                messages.error(request, 'Erreur lors de la création de l\'horaire.')
    else:
        form = HoraireForm()
    
    return render(request, 'accounts/horaire_form.html', {
        'form': form,
        'title': 'Créer un horaire',
        'submit_label': 'Créer l\'horaire',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def horaire_detail_view(request, horaire_uri):
    """Détails et modification d'un horaire"""
    from urllib.parse import unquote
    horaire_uri = unquote(horaire_uri)
    
    horaires = sparql.get_horaires()
    horaire_data = None
    
    for h in horaires:
        if h.get('horaire', '') == horaire_uri:
            horaire_data = {
                'uri': h.get('horaire', ''),
                'heureDepart': h.get('heureDepart', ''),
                'heureArrivee': h.get('heureArrivee', ''),
                'jour': h.get('jour', ''),
                'type': h.get('type', '').split('#')[-1] if h.get('type', '') else 'Horaire'
            }
            break
    
    if not horaire_data:
        messages.error(request, 'Horaire non trouvé.')
        return redirect('accounts:horaires_list')
    
    if request.method == 'POST':
        form = HoraireForm(request.POST)
        if form.is_valid():
            success = sparql.update_horaire(
                horaire_uri=horaire_uri,
                heureDepart=str(form.cleaned_data.get('heureDepart')),
                heureArrivee=str(form.cleaned_data.get('heureArrivee')),
                jour=form.cleaned_data.get('jour') or None
            )
            
            if success:
                messages.success(request, 'Horaire mis à jour avec succès!')
                return redirect('accounts:horaires_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour de l\'horaire.')
    else:
        form = HoraireForm(initial={
            'heureDepart': horaire_data['heureDepart'],
            'heureArrivee': horaire_data['heureArrivee'],
            'jour': horaire_data['jour'],
            'type_horaire': horaire_data['type']
        })
    
    return render(request, 'accounts/horaire_form.html', {
        'form': form,
        'horaire': horaire_data,
        'title': 'Modifier l\'horaire',
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def horaire_delete_view(request, horaire_uri):
    """Supprime un horaire"""
    from urllib.parse import unquote
    horaire_uri = unquote(horaire_uri)
    
    if request.method == 'POST':
        success = sparql.delete_horaire(horaire_uri)
        if success:
            messages.success(request, 'Horaire supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression de l\'horaire.')
        return redirect('accounts:horaires_list')
    
    horaires = sparql.get_horaires()
    horaire_data = None
    
    for h in horaires:
        if h.get('horaire', '') == horaire_uri:
            horaire_data = {
                'uri': h.get('horaire', ''),
                'heureDepart': h.get('heureDepart', 'N/A'),
                'heureArrivee': h.get('heureArrivee', 'N/A'),
                'jour': h.get('jour', 'Tous les jours'),
                'type': h.get('type', '').split('#')[-1] if h.get('type', '') else 'Horaire'
            }
            break
    
    if not horaire_data:
        messages.error(request, 'Horaire non trouvé.')
        return redirect('accounts:horaires_list')
    
    return render(request, 'accounts/horaire_confirm_delete.html', {
        'horaire': horaire_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES PARKINGS
# ============================================

@login_required
def parkings_list_view(request):
    """Liste tous les parkings"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'parkings': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            parkings = sparql.get_parkings()
            for p in parkings:
                context['parkings'].append({
                    'uri': p.get('parking', ''),
                    'nom': p.get('nom', 'N/A'),
                    'nombrePlaces': p.get('nombrePlaces', 'N/A'),
                    'placesDisponibles': p.get('placesDisponibles', 'N/A'),
                    'adresse': p.get('adresse', 'N/A'),
                    'latitude': p.get('latitude', 'N/A'),
                    'longitude': p.get('longitude', 'N/A'),
                    'type': p.get('type', '').split('#')[-1] if p.get('type', '') else 'Parking'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/parkings_list.html', context)


@login_required
def parking_create_view(request):
    """Crée un nouveau parking"""
    if request.method == 'POST':
        form = ParkingForm(request.POST)
        if form.is_valid():
            success = sparql.create_parking(
                nom=form.cleaned_data['nom'],
                nombrePlaces=form.cleaned_data['nombrePlaces'],
                placesDisponibles=form.cleaned_data.get('placesDisponibles'),
                adresse=form.cleaned_data.get('adresse', ''),
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude'),
                type_parking=form.cleaned_data['type_parking']
            )
            
            if success:
                messages.success(request, 'Parking créé avec succès!')
                return redirect('accounts:parkings_list')
            else:
                messages.error(request, 'Erreur lors de la création du parking.')
    else:
        form = ParkingForm()
    
    return render(request, 'accounts/parking_form.html', {
        'form': form,
        'title': 'Créer un parking',
        'submit_label': 'Créer le parking',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def parking_detail_view(request, parking_uri):
    """Détails et modification d'un parking"""
    from urllib.parse import unquote
    parking_uri = unquote(parking_uri)
    
    parkings = sparql.get_parkings()
    parking_data = None
    
    for p in parkings:
        if p.get('parking', '') == parking_uri:
            parking_data = {
                'uri': p.get('parking', ''),
                'nom': p.get('nom', ''),
                'nombrePlaces': p.get('nombrePlaces', ''),
                'placesDisponibles': p.get('placesDisponibles', ''),
                'adresse': p.get('adresse', ''),
                'type': p.get('type', '').split('#')[-1] if p.get('type', '') else 'Parking'
            }
            break
    
    if not parking_data:
        messages.error(request, 'Parking non trouvé.')
        return redirect('accounts:parkings_list')
    
    if request.method == 'POST':
        form = ParkingForm(request.POST)
        if form.is_valid():
            success = sparql.update_parking(
                parking_uri=parking_uri,
                nom=form.cleaned_data.get('nom'),
                nombrePlaces=form.cleaned_data.get('nombrePlaces'),
                placesDisponibles=form.cleaned_data.get('placesDisponibles'),
                adresse=form.cleaned_data.get('adresse', '')
            )
            
            if success:
                messages.success(request, 'Parking mis à jour avec succès!')
                return redirect('accounts:parkings_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour du parking.')
    else:
        form = ParkingForm(initial={
            'nom': parking_data['nom'],
            'type_parking': parking_data['type'],
            'nombrePlaces': parking_data['nombrePlaces'],
            'placesDisponibles': parking_data['placesDisponibles'],
            'adresse': parking_data['adresse']
        })
    
    return render(request, 'accounts/parking_form.html', {
        'form': form,
        'parking': parking_data,
        'title': f"Modifier {parking_data['nom']}",
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def parking_delete_view(request, parking_uri):
    """Supprime un parking"""
    from urllib.parse import unquote
    parking_uri = unquote(parking_uri)
    
    if request.method == 'POST':
        success = sparql.delete_parking(parking_uri)
        if success:
            messages.success(request, 'Parking supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression du parking.')
        return redirect('accounts:parkings_list')
    
    parkings = sparql.get_parkings()
    parking_data = None
    
    for p in parkings:
        if p.get('parking', '') == parking_uri:
            parking_data = {
                'uri': p.get('parking', ''),
                'nom': p.get('nom', 'N/A'),
                'nombrePlaces': p.get('nombrePlaces', 'N/A'),
                'placesDisponibles': p.get('placesDisponibles', 'N/A'),
                'adresse': p.get('adresse', 'N/A'),
                'type': p.get('type', '').split('#')[-1] if p.get('type', '') else 'Parking'
            }
            break
    
    if not parking_data:
        messages.error(request, 'Parking non trouvé.')
        return redirect('accounts:parkings_list')
    
    return render(request, 'accounts/parking_confirm_delete.html', {
        'parking': parking_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES ÉVÉNEMENTS
# ============================================

@login_required
def evenements_list_view(request):
    """Liste tous les événements de trafic"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'evenements': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            evenements = sparql.get_evenements()
            for e in evenements:
                context['evenements'].append({
                    'uri': e.get('evenement', ''),
                    'typeEvenement': e.get('typeEvenement', 'N/A'),
                    'dateEvenement': e.get('dateEvenement', 'N/A'),
                    'description': e.get('description', 'N/A'),
                    'latitude': e.get('latitude', 'N/A'),
                    'longitude': e.get('longitude', 'N/A'),
                    'type': e.get('type', '').split('#')[-1] if e.get('type', '') else 'ÉvénementTrafic'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/evenements_list.html', context)


@login_required
def evenement_create_view(request):
    """Crée un nouvel événement de trafic"""
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            date_evt = form.cleaned_data.get('dateEvenement')
            success = sparql.create_evenement(
                typeEvenement=form.cleaned_data['typeEvenement'],
                dateEvenement=date_evt.isoformat() if date_evt else None,
                description=form.cleaned_data.get('description', ''),
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude'),
                type_evt=form.cleaned_data['type_evt']
            )
            
            if success:
                messages.success(request, 'Événement créé avec succès!')
                return redirect('accounts:evenements_list')
            else:
                messages.error(request, 'Erreur lors de la création de l\'événement.')
    else:
        form = EvenementForm()
    
    return render(request, 'accounts/evenement_form.html', {
        'form': form,
        'title': 'Créer un événement',
        'submit_label': 'Créer l\'événement',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def evenement_detail_view(request, evenement_uri):
    """Détails et modification d'un événement"""
    from urllib.parse import unquote
    evenement_uri = unquote(evenement_uri)
    
    evenements = sparql.get_evenements()
    evenement_data = None
    
    for e in evenements:
        if e.get('evenement', '') == evenement_uri:
            evenement_data = {
                'uri': e.get('evenement', ''),
                'typeEvenement': e.get('typeEvenement', ''),
                'dateEvenement': e.get('dateEvenement', ''),
                'description': e.get('description', ''),
                'type': e.get('type', '').split('#')[-1] if e.get('type', '') else 'ÉvénementTrafic'
            }
            break
    
    if not evenement_data:
        messages.error(request, 'Événement non trouvé.')
        return redirect('accounts:evenements_list')
    
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            date_evt = form.cleaned_data.get('dateEvenement')
            success = sparql.update_evenement(
                evenement_uri=evenement_uri,
                typeEvenement=form.cleaned_data.get('typeEvenement'),
                dateEvenement=date_evt.isoformat() if date_evt else None,
                description=form.cleaned_data.get('description', '')
            )
            
            if success:
                messages.success(request, 'Événement mis à jour avec succès!')
                return redirect('accounts:evenements_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour de l\'événement.')
    else:
        form = EvenementForm(initial={
            'typeEvenement': evenement_data['typeEvenement'],
            'type_evt': evenement_data['type'],
            'description': evenement_data['description']
        })
    
    return render(request, 'accounts/evenement_form.html', {
        'form': form,
        'evenement': evenement_data,
        'title': 'Modifier l\'événement',
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def evenement_delete_view(request, evenement_uri):
    """Supprime un événement"""
    from urllib.parse import unquote
    evenement_uri = unquote(evenement_uri)
    
    if request.method == 'POST':
        success = sparql.delete_evenement(evenement_uri)
        if success:
            messages.success(request, 'Événement supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression de l\'événement.')
        return redirect('accounts:evenements_list')
    
    evenements = sparql.get_evenements()
    evenement_data = None
    
    for e in evenements:
        if e.get('evenement', '') == evenement_uri:
            evenement_data = {
                'uri': e.get('evenement', ''),
                'typeEvenement': e.get('typeEvenement', 'N/A'),
                'dateEvenement': e.get('dateEvenement', 'N/A'),
                'description': e.get('description', 'N/A'),
                'type': e.get('type', '').split('#')[-1] if e.get('type', '') else 'ÉvénementTrafic'
            }
            break
    
    if not evenement_data:
        messages.error(request, 'Événement non trouvé.')
        return redirect('accounts:evenements_list')
    
    return render(request, 'accounts/evenement_confirm_delete.html', {
        'evenement': evenement_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })
# ============================================
# GESTION CRUD DES CAPTEURS
# ============================================

@login_required
def capteurs_list_view(request):
    """Liste tous les capteurs"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'capteurs': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            capteurs = sparql.get_capteurs()
            for c in capteurs:
                context['capteurs'].append({
                    'uri': c.get('capteur', ''),
                    'nom': c.get('nom', 'N/A'),
                    'etat': c.get('etat', 'N/A'),
                    'latitude': c.get('latitude', 'N/A'),
                    'longitude': c.get('longitude', 'N/A'),
                    'type': c.get('type', '').split('#')[-1] if c.get('type', '') else 'Capteur'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/capteurs_list.html', context)


@login_required
def capteur_create_view(request):
    """Crée un nouveau capteur"""
    if request.method == 'POST':
        form = CapteurForm(request.POST)
        if form.is_valid():
            success = sparql.create_capteur(
                nom=form.cleaned_data['nom'],
                type_capteur=form.cleaned_data['type_capteur'],
                etat=form.cleaned_data.get('etat'),
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude')
            )
            
            if success:
                messages.success(request, 'Capteur créé avec succès!')
                return redirect('accounts:capteurs_list')
            else:
                messages.error(request, 'Erreur lors de la création du capteur.')
    else:
        form = CapteurForm()
    
    return render(request, 'accounts/capteur_form.html', {
        'form': form,
        'title': 'Créer un capteur',
        'submit_label': 'Créer le capteur',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def capteur_detail_view(request, capteur_uri):
    """Détails et modification d'un capteur"""
    from urllib.parse import unquote
    capteur_uri = unquote(capteur_uri)
    
    capteurs = sparql.get_capteurs()
    capteur_data = None
    
    for c in capteurs:
        if c.get('capteur', '') == capteur_uri:
            capteur_data = {
                'uri': c.get('capteur', ''),
                'nom': c.get('nom', ''),
                'etat': c.get('etat', ''),
                'type': c.get('type', '').split('#')[-1] if c.get('type', '') else 'Capteur'
            }
            break
    
    if not capteur_data:
        messages.error(request, 'Capteur non trouvé.')
        return redirect('accounts:capteurs_list')
    
    if request.method == 'POST':
        form = CapteurForm(request.POST)
        if form.is_valid():
            success = sparql.update_capteur(
                capteur_uri=capteur_uri,
                nom=form.cleaned_data.get('nom'),
                etat=form.cleaned_data.get('etat')
            )
            
            if success:
                messages.success(request, 'Capteur mis à jour avec succès!')
                return redirect('accounts:capteurs_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour du capteur.')
    else:
        form = CapteurForm(initial={
            'nom': capteur_data['nom'],
            'type_capteur': capteur_data['type'],
            'etat': capteur_data['etat']
        })
    
    return render(request, 'accounts/capteur_form.html', {
        'form': form,
        'capteur': capteur_data,
        'title': f"Modifier {capteur_data['nom']}",
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def capteur_delete_view(request, capteur_uri):
    """Supprime un capteur"""
    from urllib.parse import unquote
    capteur_uri = unquote(capteur_uri)
    
    if request.method == 'POST':
        success = sparql.delete_capteur(capteur_uri)
        if success:
            messages.success(request, 'Capteur supprimé avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression du capteur.')
        return redirect('accounts:capteurs_list')
    
    capteurs = sparql.get_capteurs()
    capteur_data = None
    
    for c in capteurs:
        if c.get('capteur', '') == capteur_uri:
            capteur_data = {
                'uri': c.get('capteur', ''),
                'nom': c.get('nom', 'N/A'),
                'etat': c.get('etat', 'N/A'),
                'type': c.get('type', '').split('#')[-1] if c.get('type', '') else 'Capteur'
            }
            break
    
    if not capteur_data:
        messages.error(request, 'Capteur non trouvé.')
        return redirect('accounts:capteurs_list')
    
    return render(request, 'accounts/capteur_confirm_delete.html', {
        'capteur': capteur_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES ROUTES
# ============================================

@login_required
def routes_list_view(request):
    """Liste toutes les routes"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'routes': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            routes = sparql.get_routes()
            for r in routes:
                context['routes'].append({
                    'uri': r.get('route', ''),
                    'nom': r.get('nom', 'N/A'),
                    'longueur': r.get('longueur', 'N/A'),
                    'etatRoute': r.get('etatRoute', 'N/A'),
                    'type': r.get('type', '').split('#')[-1] if r.get('type', '') else 'Route'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/routes_list.html', context)


@login_required
def route_create_view(request):
    """Crée une nouvelle route"""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            success = sparql.create_route(
                nom=form.cleaned_data['nom'],
                type_route=form.cleaned_data['type_route'],
                longueur=form.cleaned_data.get('longueur'),
                etatRoute=form.cleaned_data.get('etatRoute')
            )
            
            if success:
                messages.success(request, 'Route créée avec succès!')
                return redirect('accounts:routes_list')
            else:
                messages.error(request, 'Erreur lors de la création de la route.')
    else:
        form = RouteForm()
    
    return render(request, 'accounts/route_form.html', {
        'form': form,
        'title': 'Créer une route',
        'submit_label': 'Créer la route',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def route_detail_view(request, route_uri):
    """Détails et modification d'une route"""
    from urllib.parse import unquote
    route_uri = unquote(route_uri)
    
    routes = sparql.get_routes()
    route_data = None
    
    for r in routes:
        if r.get('route', '') == route_uri:
            route_data = {
                'uri': r.get('route', ''),
                'nom': r.get('nom', ''),
                'longueur': r.get('longueur', ''),
                'etatRoute': r.get('etatRoute', ''),
                'type': r.get('type', '').split('#')[-1] if r.get('type', '') else 'Route'
            }
            break
    
    if not route_data:
        messages.error(request, 'Route non trouvée.')
        return redirect('accounts:routes_list')
    
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            success = sparql.update_route(
                route_uri=route_uri,
                nom=form.cleaned_data.get('nom'),
                longueur=form.cleaned_data.get('longueur'),
                etatRoute=form.cleaned_data.get('etatRoute')
            )
            
            if success:
                messages.success(request, 'Route mise à jour avec succès!')
                return redirect('accounts:routes_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour de la route.')
    else:
        form = RouteForm(initial={
            'nom': route_data['nom'],
            'type_route': route_data['type'],
            'longueur': route_data['longueur'],
            'etatRoute': route_data['etatRoute']
        })
    
    return render(request, 'accounts/route_form.html', {
        'form': form,
        'route': route_data,
        'title': f"Modifier {route_data['nom']}",
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def route_delete_view(request, route_uri):
    """Supprime une route"""
    from urllib.parse import unquote
    route_uri = unquote(route_uri)
    
    if request.method == 'POST':
        success = sparql.delete_route(route_uri)
        if success:
            messages.success(request, 'Route supprimée avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression de la route.')
        return redirect('accounts:routes_list')
    
    routes = sparql.get_routes()
    route_data = None
    
    for r in routes:
        if r.get('route', '') == route_uri:
            route_data = {
                'uri': r.get('route', ''),
                'nom': r.get('nom', 'N/A'),
                'longueur': r.get('longueur', 'N/A'),
                'etatRoute': r.get('etatRoute', 'N/A'),
                'type': r.get('type', '').split('#')[-1] if r.get('type', '') else 'Route'
            }
            break
    
    if not route_data:
        messages.error(request, 'Route non trouvée.')
        return redirect('accounts:routes_list')
    
    return render(request, 'accounts/route_confirm_delete.html', {
        'route': route_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })


# ============================================
# GESTION CRUD DES VILLES
# ============================================

@login_required
def villes_list_view(request):
    """Liste toutes les villes"""
    context = {
        'fuseki_available': FUSEKI_AVAILABLE,
        'villes': []
    }
    
    if FUSEKI_AVAILABLE:
        try:
            villes = sparql.get_villes()
            for v in villes:
                context['villes'].append({
                    'uri': v.get('ville', ''),
                    'nom': v.get('nom', 'N/A'),
                    'latitude': v.get('latitude', 'N/A'),
                    'longitude': v.get('longitude', 'N/A'),
                    'type': v.get('type', '').split('#')[-1] if v.get('type', '') else 'Ville'
                })
        except Exception as e:
            context['error'] = str(e)
    
    return render(request, 'accounts/villes_list.html', context)


@login_required
def ville_create_view(request):
    """Crée une nouvelle ville"""
    if request.method == 'POST':
        form = VilleForm(request.POST)
        if form.is_valid():
            success = sparql.create_ville(
                nom=form.cleaned_data['nom'],
                type_ville=form.cleaned_data['type_ville'],
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude')
            )
            
            if success:
                messages.success(request, 'Ville créée avec succès!')
                return redirect('accounts:villes_list')
            else:
                messages.error(request, 'Erreur lors de la création de la ville.')
    else:
        form = VilleForm()
    
    return render(request, 'accounts/ville_form.html', {
        'form': form,
        'title': 'Créer une ville/zone',
        'submit_label': 'Créer la ville',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def ville_detail_view(request, ville_uri):
    """Détails et modification d'une ville"""
    from urllib.parse import unquote
    ville_uri = unquote(ville_uri)
    
    villes = sparql.get_villes()
    ville_data = None
    
    for v in villes:
        if v.get('ville', '') == ville_uri:
            ville_data = {
                'uri': v.get('ville', ''),
                'nom': v.get('nom', ''),
                'latitude': v.get('latitude', ''),
                'longitude': v.get('longitude', ''),
                'type': v.get('type', '').split('#')[-1] if v.get('type', '') else 'Ville'
            }
            break
    
    if not ville_data:
        messages.error(request, 'Ville non trouvée.')
        return redirect('accounts:villes_list')
    
    if request.method == 'POST':
        form = VilleForm(request.POST)
        if form.is_valid():
            success = sparql.update_ville(
                ville_uri=ville_uri,
                nom=form.cleaned_data.get('nom'),
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude')
            )
            
            if success:
                messages.success(request, 'Ville mise à jour avec succès!')
                return redirect('accounts:villes_list')
            else:
                messages.error(request, 'Erreur lors de la mise à jour de la ville.')
    else:
        form = VilleForm(initial={
            'nom': ville_data['nom'],
            'type_ville': ville_data['type'],
            'latitude': ville_data['latitude'],
            'longitude': ville_data['longitude']
        })
    
    return render(request, 'accounts/ville_form.html', {
        'form': form,
        'ville': ville_data,
        'title': f"Modifier {ville_data['nom']}",
        'submit_label': 'Mettre à jour',
        'fuseki_available': FUSEKI_AVAILABLE
    })


@login_required
def ville_delete_view(request, ville_uri):
    """Supprime une ville"""
    from urllib.parse import unquote
    ville_uri = unquote(ville_uri)
    
    if request.method == 'POST':
        success = sparql.delete_ville(ville_uri)
        if success:
            messages.success(request, 'Ville supprimée avec succès!')
        else:
            messages.error(request, 'Erreur lors de la suppression de la ville.')
        return redirect('accounts:villes_list')
    
    villes = sparql.get_villes()
    ville_data = None
    
    for v in villes:
        if v.get('ville', '') == ville_uri:
            ville_data = {
                'uri': v.get('ville', ''),
                'nom': v.get('nom', 'N/A'),
                'latitude': v.get('latitude', 'N/A'),
                'longitude': v.get('longitude', 'N/A'),
                'type': v.get('type', '').split('#')[-1] if v.get('type', '') else 'Ville'
            }
            break
    
    if not ville_data:
        messages.error(request, 'Ville non trouvée.')
        return redirect('accounts:villes_list')
    
    return render(request, 'accounts/ville_confirm_delete.html', {
        'ville': ville_data,
        'fuseki_available': FUSEKI_AVAILABLE
    })
