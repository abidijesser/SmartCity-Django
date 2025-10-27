# Guide d'Installation et Configuration d'Apache Fuseki

## 📋 Prérequis

- Java JDK 11 ou supérieur
- Apache Fuseki (téléchargeable depuis https://jena.apache.org/download/)

## 🔧 Installation d'Apache Fuseki

### 1. Télécharger Apache Fuseki

```bash
# Télécharger depuis le site officiel
wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.x.x.zip
```

### 2. Extraire et configurer

```bash
# Extraire l'archive
unzip apache-jena-fuseki-4.x.x.zip
cd apache-jena-fuseki-4.x.x
```

### 3. Créer un dataset

```bash
# Créer un répertoire pour le dataset
mkdir -p run/databases/transport

# Copier l'ontologie RDF
cp /path/to/ontologie.rdf run/databases/transport/ontology.owl

# Créer le fichier de configuration du dataset
cat > run/configuration/transport.ttl << EOF
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .

<#transport_dataset> rdf:type fuseki:DataService ;
    fuseki:name                        "transport" ;
    fuseki:serviceQuery                "sparql" ;
    fuseki:serviceQueryGraphStore      "data" ;
    fuseki:serviceReadWriteGraphStore  "upload" ;
    fuseki:dataset                     <#dataset> ;
    .

<#dataset> rdf:type ja:DatasetTxnMem ;
    ja:defaultGraph <#graph> ;
    .

<#graph> rdf:type ja:MemoryModel ;
    ja:content [ja:externalContent <file:databases/transport/ontology.owl>] ;
    .
EOF
```

### 4. Démarrer Fuseki

```bash
# Démarrer le serveur Fuseki
./fuseki-server
```

Le serveur sera accessible sur **http://localhost:3030**

## 🌐 Interface Web Fuseki

Une fois le serveur démarré, accédez à:
- **Interface admin**: http://localhost:3030
- **Endpoint SPARQL**: http://localhost:3030/transport/sparql
- **Query UI**: http://localhost:3030/fuseki

## 💻 Utilisation avec Django

### Configuration dans Django

```python
# settings.py
FUSEKI_URL = "http://localhost:3030/transport"
FUSEKI_QUERY_URL = "http://localhost:3030/transport/query"
FUSEKI_UPDATE_URL = "http://localhost:3030/transport/update"
```

### Exemple d'utilisation

```python
from sparql_client import SparqlClient

# Créer une instance du client
client = SparqlClient(fuseki_url="http://localhost:3030/transport/query")

# Exécuter une requête
stations = client.get_all_stations()
for station in stations:
    print(station['nom'])
```

## 🧪 Tester les Requêtes

### Requête 1: Lister toutes les stations

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?station ?nom ?latitude ?longitude
WHERE {
    ?station rdf:type transport:Station .
    OPTIONAL { ?station transport:nom ?nom . }
    OPTIONAL { ?station transport:latitude ?latitude . }
    OPTIONAL { ?station transport:longitude ?longitude . }
}
```

### Requête 2: Trouver les parkings près d'une station

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?parking ?nom ?placesDisponibles
WHERE {
    ?station transport:nom "NomStation" .
    ?station transport:procheDe ?parking .
    ?parking rdf:type transport:Parking .
    ?parking transport:nom ?nom .
    ?parking transport:placesDisponibles ?placesDisponibles .
}
```

### Requête 3: Recherche de trajets

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?trajet ?heureDepart ?heureArrivee ?vehicule
WHERE {
    ?trajet rdf:type transport:Trajet .
    ?trajet transport:aPourDepart ?depart .
    ?trajet transport:aPourArrivee ?arrivee .
    ?trajet transport:heureDepart ?heureDepart .
    ?trajet transport:heureArrivee ?heureArrivee .
    ?trajet transport:utiliseVehicule ?vehicule .
}
```

## 🚀 Commandes Utiles

```bash
# Démarrer Fuseki en arrière-plan
./fuseki-server &

# Arrêter Fuseki
pkill -f fuseki-server

# Voir les logs
tail -f logs/fuseki.log

# Nettoyer la base de données
rm -rf run/databases/transport/*
```

## 📝 Notes Importantes

1. **Port**: Par défaut, Fuseki utilise le port 3030
2. **Dataset**: Créez un dataset séparé pour chaque projet
3. **Performance**: Pour de grandes bases RDF, utilisez un backend de triplestore persistant
4. **Sécurité**: En production, configurez l'authentification

## 🔗 Ressources

- Documentation officielle: https://jena.apache.org/documentation/fuseki2/
- SPARQL 1.1: https://www.w3.org/TR/sparql11-query/
- Tutoriels: https://jena.apache.org/tutorials/

