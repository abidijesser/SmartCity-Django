# Système de Transport Intelligent - Django + Ontologie RDF

Application web Django intégrant une ontologie RDF/OWL pour le domaine du transport, avec authentification et espaces utilisateurs selon les rôles.

## 🎯 Fonctionnalités

- **Authentification complète** : Inscription, connexion, déconnexion
- **Trois types d'utilisateurs** :
  - **Conducteur** : Gestion des trajets et véhicules
  - **Passager** : Recherche de trajets et consultation des horaires
  - **Gestionnaire Transport** : Administration du système
- **Profil utilisateur** : Informations personnelles + lien vers l'ontologie RDF
- **Interfaces distinctes** : Dashboard spécifique selon le rôle

## 🏗️ Architecture

### Base de données Django (SQLite)
- **UserProfile** : Modèle étendu pour les utilisateurs avec:
  - `role` : Conducteur, Passager ou GestionnaireTransport
  - `telephone` : Numéro de téléphone
  - `linked_uri` : URI vers l'individu dans l'ontologie RDF
  
### Ontologie RDF/OWL (à venir)
L'ontologie modélisera le domaine du transport avec:

#### Classes principales
- Ville, ZoneIndustrielle, ZoneRésidentielle
- Station (StationBus, StationMetro, StationTramway)
- Véhicule (Bus, Voiture, Taxi)
- Utilisateur (Conducteur, Passager, GestionnaireTransport)
- Horaire, Trajet, Parking, Route, ÉvénementTrafic

#### Object Properties
- `aPourDepart`, `aPourArrivee`, `utiliseVehicule`
- `situeDans`, `contientStation`, `contientParking`
- `effectueTrajet`, `procheDe`, `connecteA`
- Et bien d'autres...

## 🚀 Installation

### 1. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install django
```

### 3. Créer les migrations et appliquer
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un superutilisateur (admin)
```bash
python manage.py createsuperuser
```

### 5. Lancer le serveur de développement
```bash
python manage.py runserver
```

## 📱 Utilisation

### Inscription
1. Accédez à `/signup/`
2. Remplissez le formulaire :
   - Nom d'utilisateur
   - Email
   - Téléphone (optionnel)
   - **Rôle** : Conducteur, Passager ou Gestionnaire
   - Mot de passe

### Connexion
1. Accédez à `/login/`
2. Entrez vos identifiants
3. Vous serez redirigé vers votre dashboard selon votre rôle

### Dashboard selon le rôle

#### Conducteur (`/dashboard/`)
- Vue d'ensemble des trajets
- Gestion du véhicule
- Consultation des horaires

#### Passager (`/dashboard/`)
- Recherche de trajet
- Mes trajets favoris
- Carte interactive des stations

#### Gestionnaire (`/dashboard/`)
- Gestion des véhicules
- Gestion des stations
- Planification des horaires
- Statistiques et analyses

### Profil (`/profile/`)
- Modifier l'email
- Modifier le téléphone
- Ajouter un URI RDF vers l'individu dans l'ontologie

## 🔐 Sécurité

- Les mots de passe sont **hachés** avec PBKDF2
- Aucune donnée sensible n'est stockée dans l'ontologie RDF
- L'URI RDF (`linked_uri`) est optionnel et sera utilisé plus tard pour les requêtes SPARQL

## 🔮 Prochaines étapes

1. **Intégration avec Apache Fuseki**
   - Créer l'ontologie RDF/OWL
   - Configurer Fuseki
   - Implémenter les requêtes SPARQL

2. **Fonctionnalités avancées**
   - Recherche de trajets avec requêtes SPARQL
   - Visualisation des données RDF
   - API REST pour l'ontologie

3. **Améliorations UI**
   - Carte interactive (OpenStreetMap)
   - Graphiques de trafic
   - Notifications en temps réel

## 📊 Structure du projet

```
project/
├── classProject/          # Configuration Django
│   ├── settings.py         # Paramètres de l'application
│   ├── urls.py            # URLs principales
│   └── ...
├── accounts/             # Application d'authentification
│   ├── models.py         # Modèles (UserProfile)
│   ├── views.py          # Vues (login, signup, dashboard)
│   ├── forms.py          # Formulaires
│   ├── urls.py           # URLs de l'app
│   └── admin.py          # Configuration admin
├── templates/            # Templates HTML
│   └── accounts/
│       ├── base.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard_conducteur.html
│       ├── dashboard_passager.html
│       ├── dashboard_gestionnaire.html
│       └── profile.html
├── db.sqlite3            # Base de données SQLite
└── manage.py
```

## 👥 Rôles des utilisateurs

### Conducteur
Gère ses trajets et son véhicule. Peut consulter les horaires et routes.

### Passager
Recherche des trajets, consulte les horaires et stations. Gère ses trajets favoris.

### GestionnaireTransport
Administre le système : véhicules, stations, horaires, trajets. Accès aux statistiques.

## 🛠️ Technologies utilisées

- **Django 4.2** : Framework web Python
- **SQLite** : Base de données
- **Bootstrap 5** : Interface utilisateur
- **Font Awesome** : Icônes
- **RDF/OWL** : Ontologie (à venir)
- **SPARQL** : Requêtes RDF (à venir)

## 📝 Notes importantes

- Les mots de passe sont stockés uniquement dans SQLite (hachés)
- L'ontologie RDF ne contient **jamais** de mots de passe
- Le lien entre Django et RDF se fait via le champ `linked_uri`
- Les requêtes SPARQL seront ajoutées dans une prochaine version

## 🤝 Contribution

Ce projet fait partie d'un système de transport intelligent intégrant le web sémantique.

