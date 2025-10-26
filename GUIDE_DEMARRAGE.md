# Guide de Démarrage Rapide 🚀

## Étape 1 : Installation

```bash
# Activer l'environnement virtuel (si vous en avez un)
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Installer Django (déjà fait normalement)
pip install django
```

## Étape 2 : Base de données

Les migrations ont déjà été créées et appliquées :
- ✅ `accounts/migrations/0001_initial.py` : Modèle UserProfile
- ✅ Base de données SQLite créée dans `db.sqlite3`

## Étape 3 : Créer un superutilisateur (admin Django)

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer un compte administrateur.

## Étape 4 : Lancer le serveur

```bash
python manage.py runserver
```

Le serveur sera accessible sur **http://127.0.0.1:8000/**

## Étape 5 : Tester l'application

### 1. Page d'accueil (http://127.0.0.1:8000/)
Redirige automatiquement vers `/login/` si non connecté.

### 2. Inscription (http://127.0.0.1:8000/signup/)
- Créez un compte avec un rôle (Conducteur, Passager ou Gestionnaire)
- Remplissez les champs requis
- Le système crée automatiquement un profil UserProfile

### 3. Connexion (http://127.0.0.1:8000/login/)
- Utilisez vos identifiants
- Redirection automatique vers le dashboard selon votre rôle

### 4. Dashboard
- **Conducteur** : Interface pour gérer les trajets et véhicules
- **Passager** : Interface pour rechercher des trajets
- **Gestionnaire** : Interface d'administration du système

### 5. Profil (http://127.0.0.1:8000/profile/)
- Modifier l'email
- Modifier le téléphone
- Ajouter un URI RDF (pour l'intégration future)

### 6. Admin Django (http://127.0.0.1:8000/admin/)
- Gérer les utilisateurs et profils
- Voir tous les UserProfile avec leurs rôles

## Structure des URLs

```
/                          → Redirige vers login ou dashboard
/signup/                   → Inscription
/login/                    → Connexion
/logout/                   → Déconnexion
/dashboard/                → Dashboard selon le rôle
/profile/                  → Profil utilisateur
/admin/                    → Interface d'administration
```

## Utilisateurs de test recommandés

Créez au moins un utilisateur de chaque type :

1. **Conducteur**
   - Username: `john_conducteur`
   - Rôle: Conducteur
   
2. **Passager**
   - Username: `marie_passager`
   - Rôle: Passager
   
3. **Gestionnaire**
   - Username: `admin_transport`
   - Rôle: GestionnaireTransport

## Vérifications

### ✅ Ce qui fonctionne
- [x] Inscription avec choix du rôle
- [x] Connexion / Déconnexion
- [x] Dashboard différent selon le rôle
- [x] Modification du profil
- [x] Champ `linked_uri` pour l'intégration RDF future
- [x] Messages de feedback (success/error)
- [x] Interface responsive Bootstrap 5

### 🔮 À venir (Phase 2)
- [ ] Intégration Apache Fuseki
- [ ] Ontologie RDF/OWL
- [ ] Requêtes SPARQL
- [ ] Recherche de trajets via SPARQL
- [ ] Visualisation des données RDF
- [ ] API REST pour l'ontologie

## Problèmes courants

### Erreur : "No module named 'django'"
**Solution** : Installez Django
```bash
pip install django
```

### Erreur : "TemplateDoesNotExist"
**Solution** : Vérifiez que les templates sont dans `templates/accounts/`

### Le dashboard ne change pas selon le rôle
**Solution** : Vérifiez que l'utilisateur a bien un profil UserProfile avec un rôle défini.
```bash
# Dans l'admin Django, vérifiez que le UserProfile a le champ role rempli
```

## Commandes utiles

```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Vérifier les erreurs
python manage.py check

# Lancer le serveur
python manage.py runserver

# Accéder à la console Django
python manage.py shell
```

## Exemple de données à tester

### Créer des utilisateurs de test (via l'admin ou l'interface)

1. **Conducteur**
```
Username: driver1
Email: driver@test.com
Rôle: Conducteur
Téléphone: +33 6 12 34 56 78
URI RDF: http://transport.example.org/ontology#Utilisateur_Driver1
```

2. **Passager**
```
Username: passenger1
Email: passenger@test.com
Rôle: Passager
Téléphone: +33 6 98 76 54 32
URI RDF: http://transport.example.org/ontology#Utilisateur_Passenger1
```

3. **Gestionnaire**
```
Username: manager1
Email: manager@test.com
Rôle: GestionnaireTransport
Téléphone: +33 1 23 45 67 89
URI RDF: http://transport.example.org/ontology#Utilisateur_Manager1
```

## Notes importantes

- **Les mots de passe** sont hachés avec PBKDF2 dans `db.sqlite3`
- **L'ontologie RDF** (à venir) ne contiendra JAMAIS de mots de passe
- **Le champ `linked_uri`** est optionnel et sera utilisé pour les requêtes SPARQL futures
- **Les sessions** sont stockées dans SQLite (tables `django_session`)

