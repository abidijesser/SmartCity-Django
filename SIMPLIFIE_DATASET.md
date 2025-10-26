# 🎯 Explication Simple : Dataset = Nom pour votre Base de Données

## 🤔 C'est quoi un "dataset" ?

Un **dataset** dans Fuseki = Un **nom** pour votre base de données RDF.

- C'est comme créer un nouveau dossier dans votre ordinateur
- Vous lui donnez un nom : **`transport`**
- Et vous y mettez votre fichier **`ontologie.rdf`**

**C'est tout !**

---

## 🚀 Qu'est-ce que vous devez faire ?

### 1️⃣ Ouvrir Fuseki dans le navigateur

**Ouvrez** : http://localhost:3030

---

### 2️⃣ Créer le "dataset" (le nom)

Vous verrez une page avec des boutons. Cherchez :

- **"Add dataset"** ou **"manage datasets"** ou **"Control Panel"**

Cliquez dessus.

---

### 3️⃣ Donner un nom

Quand on vous demande un nom, tapez : **`transport`**

(N'importe quel nom fonctionne, mais on utilise "transport" car c'est ce que l'application Django cherche)

---

### 4️⃣ Cliquer sur "Create" ou "Add"

C'est fait ! Vous avez créé un "dataset" nommé `transport`.

---

### 5️⃣ Uploader votre fichier `ontologie.rdf`

Maintenant, sur la même page :

1. Cherchez **"Upload"** ou un bouton de téléchargement
2. Cliquez sur **"Choose File"** ou **"Browse"**
3. Sélectionnez **`ontologie.rdf`** (fichier dans le dossier du projet)
4. Cliquez sur **"Upload"** ou **"Send"**

✅ **Votre ontologie est dans le dataset `transport` !**

---

### 6️⃣ C'est tout !

Maintenant, votre application Django peut utiliser vos données RDF !

Redémarrez Django :
```powershell
python manage.py runserver
```

Et allez sur : http://127.0.0.1:8000/dashboard/

Le message d'avertissement disparaîtra ! 🎉

---

## 💡 Analogie Simple

- **Dataset** = Un dossier
- **Nom "transport"** = Le nom du dossier
- **ontologie.rdf** = Le fichier que vous mettez dans le dossier
- **Fuseki** = L'ordinateur qui gère tout ça
- **Django** = Votre application qui lit les fichiers du dossier

---

## ✅ Résumé en 3 étapes

1. Aller sur http://localhost:3030
2. Créer un dataset nommé **`transport`**
3. Uploader le fichier **`ontologie.rdf`** dedans

C'est tout ! Le reste se fait automatiquement.

