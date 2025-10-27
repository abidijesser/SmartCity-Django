# 🚗 Guide CRUD des Véhicules

## ✅ Fonctionnalité Créée

Vous pouvez maintenant **gérer les véhicules directement depuis votre application Django** avec des formulaires et des opérations CRUD (Create, Read, Update, Delete).

---

## 🎯 Pages Disponibles

### 1️⃣ Liste des véhicules
**URL** : http://127.0.0.1:8000/vehicules/

Affiche tous les véhicules avec leurs informations :
- Nom
- Type (Bus, Taxi, etc.)
- Matricule
- Capacité (nombre de passagers)
- Vitesse moyenne
- Actions (Modifier, Supprimer)

### 2️⃣ Créer un véhicule
**URL** : http://127.0.0.1:8000/vehicules/create/

Formulaire pour créer un nouveau véhicule :
- Nom du véhicule (requis)
- Type (Bus, Taxi, Véhicule - requis)
- Matricule (optionnel)
- Capacité en passagers (optionnel)
- Vitesse moyenne en km/h (optionnel)

### 3️⃣ Modifier un véhicule
**URL** : http://127.0.0.1:8000/vehicules/{vehicule_uri}/edit/

Formulaire pré-rempli pour modifier les informations d'un véhicule existant.

### 4️⃣ Supprimer un véhicule
**URL** : http://127.0.0.1:8000/vehicules/{vehicule_uri}/delete/

Page de confirmation avant suppression.

---

## 🚀 Comment Utiliser

### Étape 1 : Accéder à la liste

Connectez-vous d'abord :
```
http://127.0.0.1:8000/login/
```

Puis allez sur :
```
http://127.0.0.1:8000/vehicules/
```

### Étape 2 : Créer un nouveau véhicule

1. Cliquez sur **"Créer un véhicule"**
2. Remplissez le formulaire :
   - **Nom** : "Bus Ligne 3"
   - **Type** : Sélectionnez "Bus"
   - **Matricule** : "TN-9876-BUS"
   - **Capacité** : 50
   - **Vitesse** : 40.5
3. Cliquez sur **"Créer le véhicule"**
4. Le véhicule est maintenant dans Fuseki !

### Étape 3 : Modifier un véhicule

1. Dans la liste, cliquez sur **"Modifier"** à côté d'un véhicule
2. Modifiez les informations
3. Cliquez sur **"Mettre à jour"**

### Étape 4 : Supprimer un véhicule

1. Dans la liste, cliquez sur **"Supprimer"** à côté d'un véhicule
2. Confirmez la suppression sur la page de confirmation
3. Le véhicule est supprimé de Fuseki

---

## 🔧 Comment ça Fonctionne

### Technologies utilisées

1. **Formulaire Django** (`VehiculeForm`)
   - Validation côté client et serveur
   - Champs avec styles Tailwind CSS
   - Champs requis/optionnels configurés

2. **Vues Django** (CRUD)
   - `vehicules_list_view()` - Liste tous les véhicules
   - `vehicule_create_view()` - Crée un nouveau véhicule
   - `vehicule_detail_view()` - Modifie un véhicule
   - `vehicule_delete_view()` - Supprime un véhicule

3. **Requêtes SPARQL** (`sparql_utils.py`)
   - `create_vehicule()` - INSERT dans Fuseki
   - `update_vehicule()` - UPDATE dans Fuseki
   - `delete_vehicule()` - DELETE dans Fuseki

### Flux de données

```
Formulaire Django
  ↓
Validation des données
  ↓
Appel méthode SPARQL
  ↓
Requête UPDATE vers Fuseki
  ↓
Données modifiées dans l'ontologie RDF
```

---

## 📋 Fichiers Créés/Modifiés

### Modifiés

- **`accounts/forms.py`**
  - Ajout de `VehiculeForm` avec tous les champs

- **`accounts/views.py`**
  - Ajout de 4 vues CRUD pour les véhicules

- **`accounts/urls.py`**
  - Ajout de 4 routes pour les URLs

- **`accounts/sparql_utils.py`**
  - Ajout de `execute_update()` pour les requêtes UPDATE
  - Ajout de `create_vehicule()`
  - Ajout de `update_vehicule()`
  - Ajout de `delete_vehicule()`

### Créés

- **`templates/accounts/vehicules_list.html`**
  - Liste des véhicules avec table

- **`templates/accounts/vehicule_form.html`**
  - Formulaire pour créer/modifier

- **`templates/accounts/vehicule_confirm_delete.html`**
  - Confirmation de suppression

---

## ✨ Avantages

### ✅ Gestion directe depuis Django
- Plus besoin d'uploader manuellement des fichiers RDF
- Interface graphique intuitive
- Validation automatique des données

### ✅ Temps réel
- Les modifications sont appliquées immédiatement dans Fuseki
- Les données RDF sont synchronisées instantanément

### ✅ Sécurité
- Seuls les utilisateurs connectés peuvent modifier
- Confirmation avant suppression

### ✅ User-friendly
- Design moderne avec Tailwind CSS
- Messages de succès/erreur
- Navigation intuitive

---

## 🎯 Exemple de Requête SPARQL Générée

Quand vous créez un véhicule "Bus Express" de type "Bus" :

```sparql
INSERT DATA {
    <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/Vehicule_Bus_Express> 
    rdf:type transport:Véhicule ;
    rdf:type transport:Bus ;
    transport:nom "Bus Express" ;
    transport:matricule "TN-EXPRESS-001" ;
    transport:capacite "50"^^xsd:integer ;
    transport:vitesseMoyenne "45.0"^^xsd:float .
}
```

Cette requête est exécutée automatiquement dans Fuseki !

---

## 🚀 Testez Maintenant

1. **Démarrez Django** :
   ```powershell
   python manage.py runserver
   ```

2. **Connectez-vous** : http://127.0.0.1:8000/login/

3. **Accédez aux véhicules** : http://127.0.0.1:8000/vehicules/

4. **Créez votre premier véhicule** !

---

## 🎉 Résultat

Vous avez maintenant un **système CRUD complet** pour gérer les véhicules directement depuis Django, sans passer par l'interface Fuseki !

**Prochaines étapes** : Appliquer le même système pour les Villes et Stations !

