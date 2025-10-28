# 📋 Fonctionnalités du Système de Transport Intelligent

## 🎯 Vue d'ensemble

Système complet de gestion de transport basé sur une ontologie RDF avec Apache Fuseki, implémentant tous les CRUDs via des requêtes SPARQL.

---

## 👤 1. GESTIONNAIRE DE TRANSPORT

### 🔧 Rôle
Administrateur du système - Configure et supervise tout le réseau de transport

### ✅ Fonctionnalités Implémentées

#### 📍 Gestion des Villes
- ✅ **Créer** une ville (`sparql.create_ville()`)
- ✅ **Lire** toutes les villes (`sparql.get_villes()`, `sparql.get_all_villes()`)
- ✅ **Modifier** une ville (`sparql.update_ville()`)
- ✅ **Supprimer** une ville (`sparql.delete_ville()`)

#### 🚏 Gestion des Stations
- ✅ **Créer** une station Bus/Tramway/Métro (`sparql.addStation()`)
- ✅ **Lire** toutes les stations (`sparql.get_all_stations()`)
- ✅ **Modifier** une station (`sparql.update_station()`)
- ✅ **Supprimer** une station (`sparql.delete_station()`)

#### 🚗 Gestion des Véhicules
- ✅ **Créer** un véhicule (`sparql.create_vehicule()`)
- ✅ **Lire** tous les véhicules (`sparql.get_vehicles()`)
- ✅ **Modifier** un véhicule (`sparql.update_vehicule()`)
- ✅ **Supprimer** un véhicule (`sparql.delete_vehicule()`)

#### 🅿️ Gestion des Parkings
- ✅ **Créer** un parking (`sparql.create_parking()`)
- ✅ **Lire** tous les parkings (`sparql.get_parkings()`)
- ✅ **Modifier** un parking (`sparql.update_parking()`)
- ✅ **Supprimer** un parking (`sparql.delete_parking()`)

#### 🛣️ Gestion des Routes
- ✅ **Créer** une route (`sparql.create_route()`)
- ✅ **Lire** toutes les routes (`sparql.get_routes()`)
- ✅ **Modifier** une route (`sparql.update_route()`)
- ✅ **Supprimer** une route (`sparql.delete_route()`)

#### ⚠️ Gestion des Événements de Trafic
- ✅ **Créer** un événement (accident, travaux, etc.) (`sparql.create_evenement()`)
- ✅ **Lire** tous les événements (`sparql.get_evenements()`, `sparql.get_traffic_events()`)
- ✅ **Modifier** un événement (`sparql.update_evenement()`)
- ✅ **Supprimer** un événement (`sparql.delete_evenement()`)

#### 📡 Gestion des Capteurs
- ✅ **Créer** un capteur (`sparql.create_capteur()`)
- ✅ **Lire** tous les capteurs (`sparql.get_capteurs()`)
- ✅ **Modifier** un capteur (`sparql.update_capteur()`)
- ✅ **Supprimer** un capteur (`sparql.delete_capteur()`)

#### 🕒 Gestion des Horaires
- ✅ **Créer** un horaire (`sparql.create_horaire()`)
- ✅ **Lire** tous les horaires (`sparql.get_horaires()`)
- ✅ **Modifier** un horaire (`sparql.update_horaire()`)
- ✅ **Supprimer** un horaire (`sparql.delete_horaire()`)

#### 📊 Supervision
- ✅ **Consulter** l'état du trafic global
- ✅ **Voir** toutes les réservations (`sparql.get_all_reservations()`)
- ✅ **Statistiques** du système (stations, véhicules, événements)

---

## 🚗 2. CONDUCTEUR

### 🔧 Rôle
Gère ses trajets et son véhicule

### ✅ Fonctionnalités Implémentées

#### 🚙 Mon Véhicule
- ✅ **Consulter** les informations de mon véhicule
  - Matricule, capacité, vitesse moyenne, type
- ✅ **Liste** de mes véhicules (`sparql.get_vehicles()`)

#### 🗺️ Mes Trajets
- ✅ **Créer** un trajet (`sparql.addTrajet()`)
  - Lieux de départ/arrivée
  - Heure de départ/arrivée
  - Distance, durée
  - Véhicule utilisé
- ✅ **Lire** mes trajets (`sparql.get_trajets_by_conducteur()`)
- ✅ **Modifier** un trajet (`sparql.update_trajet()`)
- ✅ **Supprimer** un trajet (`sparql.delete_trajet()`)

#### 🕐 Horaires
- ✅ **Associer** des horaires à mes trajets
- ✅ **Consulter** les horaires (`sparql.get_horaires()`)

#### 📈 Statistiques (NOUVEAU ✨)
- ✅ **Nombre total** de trajets effectués
- ✅ **Distance totale** parcourue
- ✅ **Durée moyenne** des trajets
- ✅ **Note moyenne** reçue des passagers
- 📊 Méthode: `sparql.get_conducteur_statistics(conducteur_uri)`

#### ⭐ Avis Reçus (NOUVEAU ✨)
- ✅ **Consulter** les avis laissés par les passagers
- 📊 Méthode: `sparql.get_avis_by_conducteur(conducteur_uri)`

---

## 🚶 3. PASSAGER

### 🔧 Rôle
Utilise le système pour planifier et réserver ses déplacements

### ✅ Fonctionnalités Implémentées

#### 🔍 Recherche de Trajets (AMÉLIORÉ ✨)
- ✅ **Recherche simple** (`sparql.search_trips()`)
  - Par station de départ
  - Par station d'arrivée
- ✅ **Recherche avancée** (`sparql.search_trajets_disponibles()`) **NOUVEAU**
  - Par ville de départ
  - Par ville d'arrivée
  - Par heure minimale
  - Affiche: horaires, distance, durée, capacité du véhicule

#### 📅 Réservations (NOUVEAU ✨)
- ✅ **Réserver** un trajet (`sparql.create_reservation()`)
  - Sélectionner le nombre de places
  - Statut: "En attente", "Confirmée", "Annulée"
- ✅ **Consulter** mes réservations (`sparql.get_reservations_by_user()`)
- ✅ **Annuler** une réservation (`sparql.delete_reservation()`)

#### 🅿️ Parkings
- ✅ **Consulter** les parkings disponibles (`sparql.get_parkings()`)
- ✅ **Voir** les places disponibles
- ✅ **Rechercher** parkings proches d'une station (`sparql.get_parkings_by_station_name()`)

#### ⭐ Avis (NOUVEAU ✨)
- ✅ **Laisser un avis** sur un trajet (`sparql.create_avis()`)
- ✅ **Laisser un avis** sur un conducteur
- ✅ **Noter** de 1 à 5 étoiles
- ✅ **Ajouter** un commentaire
- ✅ **Consulter** les avis d'un trajet (`sparql.get_avis_by_trajet()`)
- ✅ **Supprimer** mon avis (`sparql.delete_avis()`)

#### 📍 Stations et Villes
- ✅ **Consulter** toutes les stations (`sparql.get_all_stations()`)
- ✅ **Consulter** toutes les villes (`sparql.get_all_villes()`)

---

## 🔄 Scénario d'Utilisation Complet

### 1️⃣ Configuration Initiale (Gestionnaire)
```
1. Le gestionnaire crée les villes: Tunis, Ariana, Ben Arous
2. Il ajoute les stations: Station République (Tunis), Station Bardo (Ariana)
3. Il enregistre les véhicules: Bus #123, Taxi #456
4. Il configure les parkings et les capteurs
```

### 2️⃣ Planification (Conducteur)
```
1. Le conducteur enregistre son véhicule (Taxi #456)
2. Il crée un trajet:
   - Départ: Station République (Tunis)
   - Arrivée: Station Bardo (Ariana)
   - Distance: 15 km
   - Durée: 25 minutes
   - Heure départ: 08:00
3. Le trajet est maintenant disponible dans Fuseki
```

### 3️⃣ Réservation (Passager) ✨ NOUVEAU
```
1. Le passager recherche un trajet Tunis → Ariana
2. Il voit le trajet du conducteur disponible
3. Il réserve 1 place
4. Réservation créée avec statut "En attente"
5. Le conducteur peut confirmer → statut "Confirmée"
```

### 4️⃣ Trajet Effectué
```
1. Le passager monte dans le véhicule
2. Le conducteur effectue le trajet
3. Le passager descend à destination
```

### 5️⃣ Évaluation (Passager) ✨ NOUVEAU
```
1. Le passager laisse un avis:
   - Note: 5/5 étoiles
   - Commentaire: "Excellent service, très ponctuel!"
2. L'avis est enregistré dans Fuseki
3. Le conducteur peut consulter ses statistiques mises à jour
```

### 6️⃣ Supervision (Gestionnaire)
```
1. Le gestionnaire consulte les statistiques:
   - Nombre de réservations
   - Événements de trafic
   - État des capteurs
2. Si incident: il crée un événement de trafic
3. Les trajets sont ajustés en conséquence
```

---

## 🗃️ Structure de l'Ontologie RDF

### Classes Principales
```
transport:Ville
transport:Station (StationBus, StationMetro, StationTramway)
transport:Véhicule (Bus, Voiture, Taxi, Tramway)
transport:Trajet
transport:Horaire
transport:Parking
transport:Route (Autoroute, RouteRurale, RouteUrbaine)
transport:ÉvénementTrafic
transport:Capteur (CapteurStationnement, CapteurTrafic)
transport:Réservation ✨ NOUVEAU
transport:Avis ✨ NOUVEAU
```

### Propriétés Principales
```
# Géolocalisation
transport:latitude, transport:longitude, transport:adresse

# Relations
transport:situeDans, transport:procheDe
transport:aPourDepart, transport:aPourArrivee
transport:utiliseVehicule, transport:conduirePar

# Réservations ✨
transport:effectuePar, transport:concerne
transport:dateReservation, transport:nombrePlaces, transport:statut

# Avis ✨
transport:donnePar, transport:concerneTrajet, transport:concerneConducteur
transport:note, transport:commentaire, transport:dateAvis

# Caractéristiques
transport:nom, transport:type, transport:capacite
transport:heureDepart, transport:heureArrivee
transport:distanceTrajet, transport:dureeTrajet
transport:nombrePlaces, transport:placesDisponibles
```

---

## 📊 Technologies Utilisées

- **Backend**: Django (Python)
- **Base de données sémantique**: Apache Fuseki (Triplestore)
- **Langage de requête**: SPARQL 1.1
- **Ontologie**: RDF/OWL
- **Frontend**: HTML, TailwindCSS, Font Awesome
- **Auth**: Django Authentication System

---

## ✨ Nouveautés Ajoutées

### 1. Système de Réservation
- Permet aux passagers de réserver des places sur les trajets
- Gestion des statuts (En attente, Confirmée, Annulée)
- Historique des réservations par utilisateur

### 2. Système d'Avis
- Notes de 1 à 5 étoiles
- Commentaires textuels
- Avis sur les trajets et les conducteurs
- Calcul automatique de la note moyenne

### 3. Statistiques Conducteur
- Nombre total de trajets
- Distance totale parcourue
- Durée moyenne des trajets
- Note moyenne reçue

### 4. Recherche Avancée
- Recherche par ville (pas seulement par station)
- Filtrage par heure minimale
- Affichage de la capacité des véhicules

---

## 🚀 Points d'Entrée Principaux

### Fichiers Clés
- `accounts/sparql_utils.py` - Toutes les requêtes SPARQL (1350+ lignes)
- `accounts/views.py` - Logique métier Django
- `accounts/models.py` - Modèles Django (User, Profile)
- `templates/accounts/` - Templates HTML

### URLs Principales
```
/accounts/login/ - Connexion
/accounts/signup/ - Inscription
/accounts/dashboard/ - Dashboard selon le rôle
/accounts/trajets/ - Gestion des trajets
/accounts/stations/ - Gestion des stations
/accounts/vehicules/ - Gestion des véhicules
... (tous les CRUDs)
```

---

## ✅ État d'Implémentation

| Fonctionnalité | Gestionnaire | Conducteur | Passager | Status |
|---------------|-------------|------------|----------|--------|
| Villes CRUD | ✅ | ❌ | ❌ | Complet |
| Stations CRUD | ✅ | ❌ | 👀 | Complet |
| Véhicules CRUD | ✅ | 👀 | ❌ | Complet |
| Trajets CRUD | ✅ | ✅ | 🔍 | Complet |
| Parkings CRUD | ✅ | ❌ | 👀 | Complet |
| Routes CRUD | ✅ | ❌ | ❌ | Complet |
| Événements CRUD | ✅ | ❌ | ❌ | Complet |
| Capteurs CRUD | ✅ | ❌ | ❌ | Complet |
| Horaires CRUD | ✅ | ✅ | 👀 | Complet |
| **Réservations** | 👀 | ❌ | ✅ | **Nouveau** ✨ |
| **Avis** | 👀 | 👀 | ✅ | **Nouveau** ✨ |
| **Statistiques** | ✅ | ✅ | ❌ | **Nouveau** ✨ |
| **Recherche avancée** | ❌ | ❌ | ✅ | **Nouveau** ✨ |

**Légende**: ✅ CRUD complet | 👀 Lecture seule | 🔍 Recherche | ❌ Pas d'accès

---

## 📝 Notes Importantes

1. **Toutes les opérations CRUD** (sauf User/Profile) utilisent **SPARQL uniquement**
2. **Pas de base de données relationnelle** pour les données de transport
3. **Tout est stocké dans Fuseki** (Apache Jena)
4. **User et Profile** utilisent Django ORM (comme requis)
5. Les **URIs RDF** sont générés automatiquement
6. Support complet des **types spécialisés** (StationBus, Autoroute, etc.)

---

## 🎯 Prochaines Étapes Possibles

- [ ] Interface de recherche de trajets pour passagers
- [ ] Dashboard de réservations
- [ ] Page de statistiques détaillées pour conducteurs
- [ ] Notifications en temps réel
- [ ] Carte interactive avec les positions en temps réel
- [ ] Export des données en RDF/XML ou Turtle
- [ ] API REST pour applications mobiles

---

**Développé avec 💙 - Système de Transport Intelligent Basé sur le Web Sémantique**
