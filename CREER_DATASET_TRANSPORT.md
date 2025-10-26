# 🎯 Créer le Dataset "transport" dans Fuseki

## ⚠️ Le dataset "transport" n'existe pas encore

C'est pour ça que votre application Django affiche le message d'avertissement.

---

## ✅ Solution Rapide (2 minutes)

### 1️⃣ Accéder à Fuseki

Ouvrez votre navigateur :
**http://localhost:3030**

### 2️⃣ Créer le Dataset

Vous verrez l'interface principale. Choisissez **UNE** de ces méthodes :

#### Méthode A : Depuis l'accueil
1. Cliquez sur **"Add dataset"** (en haut à droite)
2. Dataset name : **`transport`**
3. Cliquez sur **"Create"** ou **"Add"**

#### Méthode B : Via Management
1. Cliquez sur **"manage datasets"** (ou "manage")
2. Cliquez sur **"Add new dataset"**
3. Dataset name : **`transport`**
4. Cliquez sur **"Create"**

### 3️⃣ Charger Votre Ontologie

Une fois le dataset créé :
1. Vous serez redirigé vers la page du dataset `transport`
2. Allez dans l'onglet **"Upload"** (ou "Data" → "Upload")
3. Cliquez sur **"Choose File"**
4. Sélectionnez **`ontologie.rdf`** (dans le dossier du projet)
5. Cliquez sur **"Upload"** ou **"Send"**

### 4️⃣ Redémarrer votre Application Django

Après le chargement, redémarrez votre serveur Django :

```powershell
python manage.py runserver
```

### 5️⃣ Vérifier

Accédez à : **http://127.0.0.1:8000/dashboard/**

✅ Le message d'avertissement disparaîtra !  
✅ Les données RDF s'afficheront !

---

## 🎯 Résumé

**Maintenant** : Fuseki démarré ✅  
**À faire** : Créer dataset + Upload ontologie  
**Ensuite** : Tout fonctionne automatiquement !

---

## 🔍 Vérifier que ça marche

Dans Fuseki → Query (dataset transport), exécutez :

```sparql
SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 10
```

Si vous voyez des résultats, c'est bon ! 🎉

