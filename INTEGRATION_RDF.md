# Intégration RDF/SPARQL avec Django

## 📋 Vue d'ensemble

Cette application Django intègre une ontologie RDF/OWL pour modéliser le domaine du transport. L'intégration se fait via Apache Fuseki et des requêtes SPARQL.

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Django App    │────────▶│  Apache Fuseki  │────────▶│  Ontologie RDF  │
│   (Python)      │ SPARQL  │  (Triplestore)  │  SPARQL  │   (ontologie.rdf)│
└─────────────────┘         └──────────────────┘         └─────────────────┘
       │
       │ SQL
       ▼
┌─────────────────┐
│  SQLite (Django) │
│  - Users         │
│  - Sessions      │
│  - Passwords     │
└─────────────────┘
```

## 🔗 Lien entre Django et RDF

### 1. Django (SQLite)
- **Utilisateurs** : Authentification Django
- **Profils** : Rôles (Conducteur, Passager, Gestionnaire)
- **Mots de passe** : Hachés avec PBKDF2
- **linked_uri** : Lien vers l'individu dans l'ontologie RDF

### 2. Ontologie RDF
- **Pas de mots de passe** : Sécurité via Django uniquement
- **Data Properties** : nom, email, telephone, latitude, longitude, etc.
- **Object Properties** : effectueTrajet, aPourDepart, situeDans, etc.
- **Classes** : Station, Véhicule, Trajet, Utilisateur, etc.

## 📝 Workflow

1. **Utilisateur s'inscrit** → Créé dans SQLite (Django)
2. **Utilisateur ajoute linked_uri** → Lien vers l'individu RDF créé dans l'ontologie
3. **Requêtes SPARQL** → Fuseki interroge l'ontologie
4. **Données affichées** → Dashboards Django affichent les données RDF

## 🚀 Utilisation

### 1. Démarrer Fuseki

```bash
# Dans le répertoire Fuseki
./fuseki-server --conf=run/configuration/transport.ttl
```

Accessible sur : http://localhost:3030

### 2. Charger l'ontologie

L'ontologie est automatiquement chargée si configurée dans `transport.ttl`

### 3. Exemple de données SPARQL

Pour créer des individus dans l'ontologie (à faire via Fuseki interface ou SPARQL UPDATE) :

#### Créer une Station

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
    transport:Station_Centre rdf:type transport:StationBus ;
        transport:nom "Centre" ;
        transport:adresse "Place de l'Étoile" ;
        transport:latitude "48.8566" ;
        transport:longitude "2.3522" .
}
```

#### Créer un Utilisateur

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT DATA {
    transport:Utilisateur_John rdf:type transport:Conducteur ;
        transport:nom "John Doe" ;
        transport:email "john@example.com" ;
        transport:telephone "0123456789" .
}
```

#### Créer un Véhicule

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT DATA {
    transport:Bus_001 rdf:type transport:Bus ;
        transport:nom "Bus Ligne 1" ;
        transport:matricule "BUS-001" ;
        transport:capacite "50" ;
        transport:vitesseMoyenne "40.0" .
}
```

## 🔍 Requêtes SPARQL Disponibles

### Liste de toutes les stations

```sparql
SELECT ?station ?nom ?adresse WHERE {
    ?station rdf:type/rdfs:subClassOf* transport:Station .
    ?station transport:nom ?nom .
    OPTIONAL { ?station transport:adresse ?adresse }
}
```

### Trajets d'un utilisateur

```sparql
SELECT ?trajet ?heureDepart ?heureArrivee WHERE {
    ?utilisateur rdf:type transport:Utilisateur .
    ?utilisateur transport:effectueTrajet ?trajet .
    ?trajet transport:heureDepart ?heureDepart .
    ?trajet transport:heureArrivee ?heureArrivee .
    FILTER (?utilisateur = transport:Utilisateur_John)
}
```

### Recherche de trajets

```sparql
SELECT ?trajet ?depart ?arrivee WHERE {
    ?trajet rdf:type transport:Trajet .
    ?trajet transport:aPourDepart ?stationDep .
    ?stationDep transport:nom ?depart .
    ?trajet transport:aPourArrivee ?stationArr .
    ?stationArr transport:nom ?arrivee .
    FILTER (CONTAINS(LCASE(?depart), "centre"))
}
```

## 📊 Modules Python

### `sparql_utils.py`
Client SPARQL pour l'ontologie de transport avec méthodes spécifiques :
- `get_all_stations()` : Liste toutes les stations
- `get_vehicles()` : Liste tous les véhicules
- `search_trips()` : Recherche de trajets
- `get_traffic_events()` : Événements de trafic

### `views.py`
Les vues Django utilisent le client SPARQL pour récupérer les données et les passer aux templates.

## 🎯 Rôles et Accès

### Conducteur
- Accès aux véhicules
- Consultation des trajets
- Gestion des horaires

### Passager
- Recherche de trajets
- Consultation des stations
- Voir les horaires

### Gestionnaire
- Vue complète (stations, véhicules, événements)
- Statistiques
- Gestion du système

## 🔒 Sécurité

- ❌ **Aucun mot de passe dans RDF**
- ✅ **Mots de passe uniquement dans SQLite (hachés)**
- ✅ **Authentification Django**
- ✅ **linked_uri relie Django → RDF**

## 📚 Ressources

- Apache Fuseki : https://jena.apache.org/documentation/fuseki2/
- SPARQL 1.1 : https://www.w3.org/TR/sparql11-query/
- Django : https://docs.djangoproject.com/

## 🛠️ Dépannage

### Fuseki ne démarre pas
```bash
# Vérifier que Java est installé
java -version

# Vérifier le port 3030
netstat -an | grep 3030
```

### Erreur de connexion
Vérifier que `FUSEKI_URL` dans `sparql_utils.py` est correct.

### Pas de données
Charger des exemples de données via SPARQL INSERT (voir exemples ci-dessus).

