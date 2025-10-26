# 🚀 Comment Démarrer Fuseki

## Option 1 : Installation Automatique

Ouvrez PowerShell dans le dossier du projet et exécutez :

```powershell
.\installe_fuseki.ps1
```

## Option 2 : Installation Manuelle

### Étape 1 : Télécharger Fuseki

Téléchargez depuis : https://jena.apache.org/download/

Ou avec PowerShell :

```powershell
cd C:\
mkdir fuseki -Force
cd fuseki
Invoke-WebRequest -Uri "https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.10.0.zip" -OutFile "fuseki.zip"
Expand-Archive -Path fuseki.zip -DestinationPath .
```

### Étape 2 : Démarrer Fuseki

```powershell
cd C:\fuseki\apache-jena-fuseki-4.10.0
.\fuseki-server
```

### Étape 3 : Vérifier

Ouvrez votre navigateur : http://localhost:3030

### Étape 4 : Créer le Dataset

1. Cliquez sur "manage datasets"
2. Créez un dataset nommé `transport`

### Étape 5 : Charger les Données

Suivez `GUIDE_CHARGEMENT_DONNEES.md` pour charger `donnees_test.rdf`

---

## 🎯 Ensuite

Une fois Fuseki démarré, votre application Django affichera automatiquement les données RDF !

Accessible sur : http://localhost:3030

