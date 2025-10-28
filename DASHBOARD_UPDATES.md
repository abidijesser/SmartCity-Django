# 📊 Dashboard Updates - Résumé des Modifications

## ✅ Modifications Effectuées

### 🚗 **1. CONDUCTEUR Dashboard**

#### ✨ Actions Principales (3 cards)
- ✅ **Mes Trajets** - Créer, modifier, gérer ses trajets
- ✅ **Mon Véhicule** - Consulter informations du véhicule
- ✅ **Mes Statistiques** ⭐ NOUVEAU - Performance, distance, notes

#### 📋 Informations Utiles (4 cards)
- ✅ **Horaires** - Consulter les horaires
- ✅ **Stations** - Voir les stations (lecture seule)
- ✅ **Alertes Trafic** - Incidents actuels (lecture seule)
- ✅ **Mes Avis** ⭐ NOUVEAU - Avis reçus des passagers

#### 📊 Stats rapides (4 widgets)
- Mes Véhicules (nombre)
- Mes Trajets (nombre)
- Distance Totale (km)
- Note Moyenne (★)

#### ❌ SUPPRIMÉ (car non accessible au conducteur)
- ❌ Parkings (gestion)
- ❌ Routes (gestion)
- ❌ Capteurs (gestion)
- ❌ Villes (gestion)

---

### 🚶 **2. PASSAGER Dashboard**

#### ✨ Actions Principales (3 cards)
- ✅ **Rechercher un Trajet** ⭐ AMÉLIORÉ - Recherche avancée (ville, station, horaire)
- ✅ **Mes Réservations** ⭐ NOUVEAU - Consulter et gérer mes réservations
- ✅ **Stations** - Consulter toutes les stations

#### 📋 Services Utiles (3 cards)
- ✅ **Horaires** - Consulter les horaires
- ✅ **Parkings** - Places disponibles
- ✅ **Alertes Trafic** - Incidents actuels

#### 📊 Stats rapides (3 widgets)
- Stations Disponibles
- Trajets Disponibles
- Mes Favoris

#### ❌ SUPPRIMÉ (car non accessible au passager)
- ❌ Carte Interactive (non implémentée)
- ❌ Villes (gestion)
- ❌ Toutes les fonctions CRUD (sauf réservations et avis)

---

### 👤 **3. GESTIONNAIRE Dashboard**

#### ✅ INCHANGÉ
Le gestionnaire garde toutes ses fonctionnalités car il a accès à TOUT :
- Gérer les Stations
- Gérer les Véhicules
- Gérer les Trajets
- + Horaires, Parkings, Routes, Événements, Capteurs, Villes

---

## 🔗 URLs à Ajouter dans `urls.py`

Les nouvelles fonctionnalités nécessitent ces URLs :

```python
# accounts/urls.py

urlpatterns = [
    # ... existant ...
    
    # === NOUVELLES URLs PASSAGER ===
    # Recherche avancée de trajets
    path('search-trajets/', views.search_trajets_view, name='search_trajets'),
    
    # Réservations
    path('reservations/', views.mes_reservations_view, name='mes_reservations'),
    path('reserver/<str:trajet_uri>/', views.reserver_trajet_view, name='reserver_trajet'),
    path('annuler-reservation/<str:reservation_uri>/', views.annuler_reservation_view, name='annuler_reservation'),
    
    # Avis (passager donne un avis)
    path('laisser-avis/<str:trajet_uri>/', views.laisser_avis_view, name='laisser_avis'),
    
    # === NOUVELLES URLs CONDUCTEUR ===
    # Statistiques conducteur
    path('mes-statistiques/', views.mes_statistiques_view, name='mes_statistiques'),
    
    # Avis reçus par le conducteur
    path('mes-avis-recus/', views.mes_avis_recus_view, name='mes_avis_recus'),
    
    # Confirmer une réservation
    path('confirmer-reservation/<str:reservation_uri>/', views.confirmer_reservation_view, name='confirmer_reservation'),
    
    # === NOUVELLES URLs GESTIONNAIRE ===
    # Toutes les réservations (supervision)
    path('toutes-reservations/', views.toutes_reservations_view, name='toutes_reservations'),
]
```

---

## 📄 Vues (Views) à Créer dans `views.py`

### 🚶 **PASSAGER Views**

```python
# === RECHERCHE AVANCÉE ===
@login_required
def search_trajets_view(request):
    """Recherche avancée de trajets par ville, station, horaire"""
    if request.method == 'POST':
        ville_depart = request.POST.get('ville_depart', '')
        ville_arrivee = request.POST.get('ville_arrivee', '')
        heure_min = request.POST.get('heure_min', '')
        
        trajets = sparql.search_trajets_disponibles(
            ville_depart=ville_depart,
            ville_arrivee=ville_arrivee,
            heure_min=heure_min
        )
        return render(request, 'accounts/search_trajets.html', {
            'trajets': trajets,
            'ville_depart': ville_depart,
            'ville_arrivee': ville_arrivee,
        })
    
    # GET: Afficher le formulaire de recherche
    villes = sparql.get_all_villes()
    return render(request, 'accounts/search_trajets.html', {
        'villes': villes
    })


# === RÉSERVATIONS ===
@login_required
def mes_reservations_view(request):
    """Afficher toutes mes réservations"""
    user_uri = f"{sparql.TRANSPORT_PREFIX}User_{request.user.username}"
    reservations = sparql.get_reservations_by_user(user_uri)
    
    return render(request, 'accounts/mes_reservations.html', {
        'reservations': reservations
    })


@login_required
def reserver_trajet_view(request, trajet_uri):
    """Réserver un trajet"""
    from urllib.parse import unquote
    trajet_uri = unquote(trajet_uri)
    
    if request.method == 'POST':
        nombre_places = int(request.POST.get('nombre_places', 1))
        user_uri = f"{sparql.TRANSPORT_PREFIX}User_{request.user.username}"
        
        success = sparql.create_reservation(
            user_uri=user_uri,
            trajet_uri=trajet_uri,
            nombre_places=nombre_places
        )
        
        if success:
            messages.success(request, 'Réservation effectuée avec succès!')
        else:
            messages.error(request, 'Erreur lors de la réservation.')
        
        return redirect('accounts:mes_reservations')
    
    # GET: Afficher le formulaire de réservation
    return render(request, 'accounts/reserver_trajet.html', {
        'trajet_uri': trajet_uri
    })


@login_required
def annuler_reservation_view(request, reservation_uri):
    """Annuler une réservation"""
    from urllib.parse import unquote
    reservation_uri = unquote(reservation_uri)
    
    if request.method == 'POST':
        success = sparql.delete_reservation(reservation_uri)
        
        if success:
            messages.success(request, 'Réservation annulée.')
        else:
            messages.error(request, 'Erreur lors de l\'annulation.')
    
    return redirect('accounts:mes_reservations')


# === AVIS ===
@login_required
def laisser_avis_view(request, trajet_uri):
    """Laisser un avis sur un trajet"""
    from urllib.parse import unquote
    trajet_uri = unquote(trajet_uri)
    
    if request.method == 'POST':
        note = int(request.POST.get('note', 5))
        commentaire = request.POST.get('commentaire', '')
        user_uri = f"{sparql.TRANSPORT_PREFIX}User_{request.user.username}"
        
        success = sparql.create_avis(
            user_uri=user_uri,
            trajet_uri=trajet_uri,
            note=note,
            commentaire=commentaire
        )
        
        if success:
            messages.success(request, 'Avis enregistré. Merci!')
        else:
            messages.error(request, 'Erreur lors de l\'enregistrement de l\'avis.')
        
        return redirect('accounts:mes_reservations')
    
    # GET: Afficher le formulaire d'avis
    return render(request, 'accounts/laisser_avis.html', {
        'trajet_uri': trajet_uri
    })
```

### 🚗 **CONDUCTEUR Views**

```python
# === STATISTIQUES ===
@login_required
def mes_statistiques_view(request):
    """Afficher mes statistiques de conducteur"""
    if not request.user.profile.is_conducteur():
        messages.error(request, 'Accès réservé aux conducteurs.')
        return redirect('accounts:dashboard')
    
    conducteur_uri = f"{sparql.TRANSPORT_PREFIX}User_{request.user.username}"
    
    # Récupérer les statistiques
    stats = sparql.get_conducteur_statistics(conducteur_uri)
    
    # Récupérer l'historique des trajets
    trajets = sparql.get_trajets_by_conducteur(conducteur_uri)
    
    # Récupérer les avis reçus
    avis = sparql.get_avis_by_conducteur(conducteur_uri)
    
    return render(request, 'accounts/mes_statistiques.html', {
        'stats': stats,
        'trajets': trajets,
        'avis': avis
    })


# === AVIS REÇUS ===
@login_required
def mes_avis_recus_view(request):
    """Afficher les avis reçus"""
    if not request.user.profile.is_conducteur():
        messages.error(request, 'Accès réservé aux conducteurs.')
        return redirect('accounts:dashboard')
    
    conducteur_uri = f"{sparql.TRANSPORT_PREFIX}User_{request.user.username}"
    avis = sparql.get_avis_by_conducteur(conducteur_uri)
    
    return render(request, 'accounts/mes_avis_recus.html', {
        'avis': avis
    })


# === CONFIRMER RÉSERVATION ===
@login_required
def confirmer_reservation_view(request, reservation_uri):
    """Confirmer une réservation (conducteur)"""
    from urllib.parse import unquote
    reservation_uri = unquote(reservation_uri)
    
    if request.method == 'POST':
        success = sparql.update_reservation_status(
            reservation_uri=reservation_uri,
            statut="Confirmée"
        )
        
        if success:
            messages.success(request, 'Réservation confirmée!')
        else:
            messages.error(request, 'Erreur lors de la confirmation.')
    
    return redirect('accounts:mes_statistiques')
```

### 👤 **GESTIONNAIRE Views**

```python
# === SUPERVISION RÉSERVATIONS ===
@login_required
def toutes_reservations_view(request):
    """Voir toutes les réservations (gestionnaire)"""
    if not request.user.profile.is_gestionnaire():
        messages.error(request, 'Accès réservé aux gestionnaires.')
        return redirect('accounts:dashboard')
    
    reservations = sparql.get_all_reservations()
    
    return render(request, 'accounts/toutes_reservations.html', {
        'reservations': reservations
    })
```

---

## 📋 Templates à Créer

### Templates Passager
```
templates/accounts/
├── search_trajets.html           # Formulaire de recherche avancée
├── mes_reservations.html         # Liste de mes réservations
├── reserver_trajet.html          # Formulaire de réservation
└── laisser_avis.html            # Formulaire d'avis
```

### Templates Conducteur
```
templates/accounts/
├── mes_statistiques.html         # Dashboard statistiques
└── mes_avis_recus.html          # Liste des avis reçus
```

### Templates Gestionnaire
```
templates/accounts/
└── toutes_reservations.html     # Supervision des réservations
```

---

## 🎯 Fonctionnalités par Rôle - Résumé Final

### 🚶 **PASSAGER** peut:
✅ Rechercher trajets (avancé)
✅ Réserver un trajet
✅ Voir mes réservations
✅ Annuler une réservation
✅ Laisser un avis
✅ Consulter: stations, horaires, parkings, événements (lecture seule)

❌ Ne peut PAS: Créer/modifier/supprimer des entités du système

---

### 🚗 **CONDUCTEUR** peut:
✅ CRUD sur MES trajets
✅ Voir MON véhicule (lecture seule)
✅ Voir MES statistiques
✅ Voir MES avis reçus
✅ Confirmer des réservations
✅ Consulter: stations, horaires, événements (lecture seule)

❌ Ne peut PAS: Gérer villes, stations, parkings, routes, capteurs, événements

---

### 👤 **GESTIONNAIRE** peut:
✅ CRUD complet sur TOUTES les entités
✅ Superviser TOUTES les réservations
✅ Gérer: villes, stations, véhicules, trajets, parkings, routes, événements, capteurs, horaires
✅ Consulter toutes les statistiques du système

---

## 📝 Prochaines Étapes

1. ✅ Dashboards mis à jour ✓
2. ⏳ Créer les URLs dans `urls.py`
3. ⏳ Créer les views dans `views.py`
4. ⏳ Créer les templates HTML
5. ⏳ Tester chaque fonctionnalité
6. ⏳ Ajouter les contrôles de permissions (@login_required, role checks)

---

**Toutes les fonctionnalités SPARQL sont prêtes dans `sparql_utils.py` !** 🎉
