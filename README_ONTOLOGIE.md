# 🚀 Utiliser votre Ontologie dans Fuseki

## ✅ Votre fichier `ontologie.rdf` est détecté !

Votre ontologie personnelle est prête à être utilisée.

---

## 📋 Étapes Simples

### 1️⃣ Accéder à Fuseki
**Ouvrez** : http://localhost:3030

### 2️⃣ Créer le Dataset
1. Cliquez sur **"manage datasets"** ou **"Add dataset"**
2. Dataset name : **`transport`**
3. Cliquez sur **"Create"** ou **"Add"**

### 3️⃣ Charger Votre Ontologie
1. Sélectionnez le dataset **`transport`**
2. Onglet **"Upload"** (ou **"Data"** → **"Upload"**)
3. Choisissez : **`ontologie.rdf`** (fichier dans le projet)
4. Cliquez sur **"Upload"** ou **"Send"**

✅ Votre ontologie est chargée !

### 4️⃣ Tester avec Django

```powershell
# Dans le terminal
python test_sparql.py
```

Ou redémarrez le serveur Django :
```powershell
python manage.py runserver
```

Puis accédez au dashboard : http://127.0.0.1:8000/dashboard/

---

## 📊 Ce que votre Application Django Fait

Une fois l'ontologie chargée, les dashboards afficheront automatiquement :

- **Conducteur** : Ses véhicules, trajets, horaires
- **Passager** : Stations, trajets disponibles, carte interactive  
- **Gestionnaire** : Toutes les stations, tous les véhicules, événements de trafic

**Tout est automatique !** ✨

---

## 🔍 Vérifier les Données dans Fuseki

Dans Fuseki → **"Query"**, exécutez :

```sparql
SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 10
```

Vous verrez les triples de votre ontologie !

---

## 🎯 Fichiers Utiles

- **`ontologie.rdf`** : Votre ontologie à charger
- **`test_sparql.py`** : Script de test de connexion
- **`CHARGER_DONNEES_FUSEKI.md`** : Guide détaillé

---

## ✅ Status Actuel

- ✅ Fuseki installé et démarré
- ✅ `ontologie.rdf` détecté
- ⏳ En attente : Création du dataset `transport`
- ⏳ En attente : Upload de l'ontologie

**Après ces 2 dernières étapes, tout fonctionne !** 🎉

