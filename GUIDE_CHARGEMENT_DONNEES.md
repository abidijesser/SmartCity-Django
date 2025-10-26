# Guide de Chargement des Données dans Fuseki

## 📋 Vue d'ensemble

Ce guide vous montre comment charger les données de test dans Apache Fuseki pour que votre application Django puisse les afficher.

## 🚀 Méthode 1 : Via l'Interface Web Fuseki (Facile)

### Étape 1 : Démarrer Fuseki
```powershell
cd C:\fuseki\apache-jena-fuseki-x.x.x
.\fuseki-server
```

### Étape 2 : Accéder à l'interface
Ouvrez votre navigateur : http://localhost:3030

### Étape 3 : Créer un nouveau dataset
1. Cliquez sur "Add dataset"
2. Nom : `transport`
3. Cliquez sur "Create dataset"

### Étape 4 : Charger les données via SPARQL INSERT
1. Allez sur : http://localhost:3030/fuseki
2. Sélectionnez le dataset `transport`
3. Cliquez sur "Query" ou "Data"
4. Copiez et exécutez le code SPARQL fourni dans `insert_donnees_test.sparql`

---

## 🚀 Méthode 2 : Via le Fichier RDF (Recommandé)

### Étape 1 : Copier le fichier
```powershell
Copy-Item "donnees_test.rdf" -Destination "C:\fuseki\run\databases\transport\"
```

### Étape 2 : Charger via l'interface Fuseki
1. Allez sur http://localhost:3030
2. Sélectionnez le dataset `transport`
3. Cliquez sur "Upload"
4. Sélectionnez le fichier `donnees_test.rdf`
5. Cliquez sur "Upload"

---

## 🚀 Méthode 3 : Via curl (Avancé)

```powershell
# Charger le fichier RDF via l'API Fuseki
$file = "donnees_test.rdf"
$content = Get-Content $file -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)

Invoke-WebRequest -Uri "http://localhost:3030/transport/data" `
    -Method POST `
    -Headers @{"Content-Type"="application/rdf+xml"} `
    -Body $bytes
```

---

## ✅ Vérifier que les données sont chargées

### Via l'interface Web
1. Allez sur http://localhost:3030
2. Sélectionnez `transport`
3. Cliquez sur "Query"
4. Exécutez cette requête :

```sparql
SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 10
```

Vous devriez voir les triples chargés !

### Via votre application Django
1. Accédez à http://127.0.0.1:8000/login/
2. Connectez-vous
3. Accédez au dashboard
4. Les données RDF devraient s'afficher ! 🎉

---

## 🔧 Dépannage

### Problème : "Connection refused"
**Solution** : Vérifiez que Fuseki est bien démarré sur le port 3030
```powershell
netstat -an | findstr :3030
```

### Problème : "Dataset not found"
**Solution** : Créez le dataset via l'interface web http://localhost:3030

### Problème : Les données ne s'affichent pas
**Solution** : Vérifiez les logs de Fuseki et les erreurs dans le terminal Django

---

## 📊 Structure des Données Chargées

Les données de test incluent :
- ✅ **3 Stations** : Centre, Ariana, République
- ✅ **3 Véhicules** : Bus_001, Bus_002, Taxi_001
- ✅ **3 Utilisateurs** : Conducteur, Passager, Gestionnaire
- ✅ **2 Trajets** : Centre↔Ariana
- ✅ **1 Horaire** : HoraireBus
- ✅ **1 Ville** : Tunis
- ✅ **2 Parkings** : ParkingPublic, ParkingPrivé
- ✅ **1 Route** : Autoroute Tunis-Ariana
- ✅ **3 Événements** : Accident, Travaux, Embouteillage

---

## 🎯 Prochaines Étapes

Après avoir chargé les données :
1. ✅ Redémarrez votre serveur Django (si nécessaire)
2. ✅ Accédez au dashboard
3. ✅ Les données RDF s'afficheront automatiquement !

