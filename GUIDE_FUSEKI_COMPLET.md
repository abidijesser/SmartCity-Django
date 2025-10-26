# Guide Complet d'Installation Apache Fuseki

## 📦 Étape 1 : Télécharger Apache Fuseki

### Option A : Depuis le site officiel
1. Aller sur : https://jena.apache.org/download/
2. Télécharger `apache-jena-fuseki-x.x.x.zip`
3. Extraire l'archive dans un dossier (ex: `C:\fuseki`)

### Option B : Via PowerShell
```powershell
# Aller dans un dossier de travail
cd C:\
mkdir fuseki
cd fuseki

# Télécharger (exemple avec PowerShell 5.1+)
Invoke-WebRequest -Uri "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.x.x.zip" -OutFile "fuseki.zip"

# Extraire
Expand-Archive -Path fuseki.zip -DestinationPath .
```

## 🔧 Étape 2 : Créer le Dataset

### Créer les répertoires
```powershell
cd C:\fuseki\apache-jena-fuseki-x.x.x
mkdir run\databases\transport
mkdir run\configuration
```

### Copier votre ontologie
```powershell
Copy-Item "C:\Users\DELL\Desktop\5TWIN6\web semantique\ontologie.rdf" -Destination "run\databases\transport\ontology.rdf"
```

## 📝 Étape 3 : Configuration du Dataset

Créer le fichier `run/configuration/transport.ttl` :

```turtle
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

<#graph> rdf:type ja:MemoryModel .
```

**OU** utiliser cette configuration simplifiée pour charger automatiquement l'ontologie :

```turtle
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .

<#transport_dataset> rdf:type fuseki:DataService ;
    fuseki:name                        "transport" ;
    fuseki:serviceQuery                "sparql" ;
    fuseki:serviceQueryGraphStore      "data" ;
    fuseki:serviceReadWriteGraphStore  "upload" ;
    fuseki:serviceUpdate               "update" ;
    fuseki:dataset                     <#dataset> ;
    .

<#dataset> rdf:type ja:DatasetTxnMem ;
    ja:defaultGraph <#graph> ;
    .

<#graph> rdf:type ja:MemoryModel .
```

## 🚀 Étape 4 : Démarrer Fuseki

```powershell
# Dans le répertoire Fuseki
.\fuseki-server --conf=run\configuration\transport.ttl
```

Ou avec l'ontologie pré-chargée :

```powershell
.\fuseki-server --tdb2 --loc=run/databases/transport transport
```

## 🌐 Étape 5 : Accéder à Fuseki

Une fois démarré, accédez à :
- **Interface Web** : http://localhost:3030
- **Query UI** : http://localhost:3030/fuseki
- **Endpoint SPARQL** : http://localhost:3030/transport/sparql

## 💾 Étape 6 : Charger des Données de Test

Utilisez l'interface web de Fuseki (http://localhost:3030) pour charger des données via SPARQL INSERT.

Ou copiez le fichier `donnees_test.rdf` que je vais créer et chargez-le via l'interface.

## 🔍 Tester la Connexion

Une fois Fuseki démarré, votre application Django récupérera automatiquement les données RDF via les requêtes SPARQL configurées.

---

**Note** : Par défaut, le port 3030 est utilisé. Assurez-vous qu'aucun autre service n'utilise ce port.

