# 🚀 Guide de Démarrage Rapide - Fuseki + Django

## ✅ Checklist Complète

### 📦 Étape 1 : Télécharger Apache Fuseki

```powershell
# Dans C:\
cd C:\
mkdir fuseki
cd fuseki

# Télécharger Fuseki
Invoke-WebRequest -Uri "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.10.0.zip" -OutFile "fuseki.zip"

# Extraire
Expand-Archive -Path fuseki.zip -DestinationPath .
```

### 📁 Étape 2 : Configurer Fuseki

```powershell
# Dans C:\fuseki\apache-jena-fuseki-4.10.0
mkdir run\databases\transport
mkdir run\configuration

# Copier l'ontologie
Copy-Item "C:\Users\DELL\Desktop\5TWIN6\web semantique\ontologie.rdf" -Destination "run\databases\transport\ontology.rdf"
```

### 📝 Étape 3 : Créer transport.ttl

Créer le fichier `run\configuration\transport.ttl` :

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

### 🚀 Étape 4 : Démarrer Fuseki

```powershell
.\fuseki-server
```

Ou en arrière-plan :

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\fuseki-server"
```

### ✅ Étape 5 : Vérifier Fuseki

Ouvrez: http://localhost:3030

Vous devriez voir l'interface de gestion Fuseki.

### 💾 Étape 6 : Charger les Données de Test

#### Option A : Via l'interface web
1. Allez sur http://localhost:3030
2. Créez un dataset nommé `transport`
3. Cliquez sur "Query"
4. Collez et exécutez le contenu de `insert_donnees_test.sparql`

#### Option B : Via upload
1. Allez sur http://localhost:3030
2. Sélectionnez le dataset `transport`
3. Cliquez sur "Upload"
4. Sélectionnez `donnees_test.rdf`

#### Option C : Via PowerShell
```powershell
cd "C:\Users\DELL\Desktop\5TWIN6\web semantique\project"
Copy-Item "donnees_test.rdf" -Destination "C:\fuseki\run\databases\transport\data.rdf"
```

Puis dans l'interface Fuseki :
- Upload le fichier `data.rdf`

### 🔍 Étape 7 : Tester avec Django

```powershell
# Dans le projet Django
cd "C:\Users\DELL\Desktop\5TWIN6\web semantique\project"
python test_sparql.py
```

### 🎉 Étape 8 : Tester l'Application

1. Démarrer Django :
```powershell
python manage.py runserver
```

2. Accéder au dashboard : http://127.0.0.1:8000/dashboard/

3. Les données RDF devraient s'afficher ! ✨

---

## 🔧 Commandes Utiles

### Démarrer Fuseki
```powershell
cd C:\fuseki\apache-jena-fuseki-4.10.0
.\fuseki-server --conf=run\configuration\transport.ttl
```

### Tester la connexion
```powershell
python test_sparql.py
```

### Voir les données
Aller sur : http://localhost:3030/fuseki

### Arrêter Fuseki
Dans le terminal Fuseki : `CTRL+C`

---

## 📊 Données de Test Incluses

✅ **3 Stations** : Centre, Ariana, République  
✅ **3 Véhicules** : Bus_001, Bus_002, Taxi_001  
✅ **3 Utilisateurs** : Conducteur, Passager, Gestionnaire  
✅ **2 Trajets** : Centre↔Ariana  
✅ **1 Ville** : Tunis  
✅ **2 Parkings** : ParkingPublic, ParkingPrivé  
✅ **3 Événements** : Accident, Travaux, Embouteillage  

---

## 🎯 Résultat Final

Une fois tout configuré :
- ✅ Fuseki accessible sur http://localhost:3030
- ✅ Dataset `transport` créé
- ✅ Données chargées
- ✅ Django peut lire les données via SPARQL
- ✅ Dashboards affichent les données RDF

Votre application est maintenant **100% fonctionnelle** avec intégration RDF/OWL ! 🎉

