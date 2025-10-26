# 🧪 Guide des Pages de Test RDF/Fuseki

## ✅ Ce qui a été créé

Pages de test pour vérifier que Django peut récupérer et afficher les données RDF depuis Fuseki.

### Pages créées :

1. **Page d'accueil des tests** : `/test/`
2. **Test Villes** : `/test/villes/` - Liste toutes les villes avec coordonnées
3. **Test Véhicules** : `/test/vehicules/` - Liste tous les véhicules avec type et capacité
4. **Test Stations** : `/test/stations/` - Liste toutes les stations avec adresse

---

## 🚀 Comment Accéder

### 1️⃣ Se connecter

Assurez-vous d'être connecté à l'application :
- Allez sur : http://127.0.0.1:8000/login/
- Connectez-vous avec vos identifiants

### 2️⃣ Accéder aux pages de test

Après connexion, utilisez ces URLs :

- **Page d'accueil des tests** : 
  ```
  http://127.0.0.1:8000/test/
  ```

- **Test Villes** : 
  ```
  http://127.0.0.1:8000/test/villes/
  ```

- **Test Véhicules** : 
  ```
  http://127.0.0.1:8000/test/vehicules/
  ```

- **Test Stations** : 
  ```
  http://127.0.0.1:8000/test/stations/
  ```

---

## 📊 Ce que vous verrez

### Si Fuseki est **disponible** et **contient des données** :

Vous verrez :
- ✅ Un message vert : "Fuseki est disponible"
- ✅ Des tableaux avec les données RDF en temps réel
- ✅ Les colonnes varient selon la page (nom, coordonnées, type, etc.)

### Si **aucune donnée** n'est trouvée :

Vous verrez :
- ✅ Un message vert : "Fuseki est disponible"
- ⚠️ Un message : "Aucun [ville/véhicule/station] trouvé"
- ℹ️ Vérifiez que des individus existent dans votre ontologie

### Si Fuseki est **indisponible** :

Vous verrez :
- ❌ Un message rouge : "Fuseki n'est pas disponible"
- ℹ️ Démarrez le serveur Fuseki sur http://localhost:3030

---

## 🔍 Comment Fonctionne

### 1. Requêtes SPARQL

Chaque page de test exécute une requête SPARQL différente :

- **Villes** : Récupère toutes les instances de type `transport:Ville`
- **Véhicules** : Récupère toutes les instances de type `transport:Véhicule`
- **Stations** : Récupère toutes les instances de type `transport:Station`

### 2. Affichage

Les résultats sont affichés dans des tableaux HTML avec :
- En-têtes clairs
- Formatage moderne avec Tailwind CSS
- Responsive (mobile/tablet/desktop)

### 3. Données en temps réel

Chaque requête lit directement depuis Fuseki en temps réel.

---

## 📝 Exemple de Requête SPARQL

Pour les villes, la requête est :

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>

SELECT ?ville ?nom ?latitude ?longitude
WHERE {
    ?ville rdf:type transport:Ville .
    ?ville transport:nom ?nom .
    OPTIONAL { ?ville transport:latitude ?latitude . }
    OPTIONAL { ?ville transport:longitude ?longitude . }
}
ORDER BY ?nom
```

---

## ⚙️ Configuration Technique

### Fichiers modifiés/créés :

1. **accounts/views.py** : Ajout de 4 nouvelles vues (test_home_view, test_villes_view, test_vehicules_view, test_stations_view)
2. **accounts/urls.py** : Ajout de 4 nouvelles routes
3. **templates/accounts/test_home.html** : Page d'accueil des tests
4. **templates/accounts/test_villes.html** : Affichage des villes
5. **templates/accounts/test_vehicules.html** : Affichage des véhicules
6. **templates/accounts/test_stations.html** : Affichage des stations

### Utilisation de la classe SPARQL existante

Les nouvelles vues utilisent le client SPARQL déjà configuré dans `accounts/sparql_utils.py` :
- `sparql.execute_query(query)` : Exécute une requête SPARQL
- `FUSEKI_AVAILABLE` : Vérifie si Fuseki est accessible

---

## 🎯 Prochaines Étapes

### Pour avoir des données à afficher :

1. **Uploader des instances dans Fuseki**
   - Allez sur http://localhost:3030
   - Sélectionnez le dataset `transport`
   - Uploadez un fichier avec des individus (villes, véhicules, stations)

2. **Ou utiliser les données de test**
   - Uploadez `donnees_test.rdf` dans Fuseki
   - Les pages de test afficheront immédiatement les données

### Pour intégrer dans le dashboard :

Une fois les tests validés, vous pouvez intégrer les mêmes requêtes dans le dashboard principal (`accounts/dashboard_moderne.html`).

---

## ✅ Résultat

**Vous avez maintenant** :
- ✅ 4 pages de test fonctionnelles
- ✅ Accès aux données RDF en temps réel
- ✅ Interface moderne avec design cohérent
- ✅ Gestion des erreurs robuste
- ✅ Messages informatifs selon l'état de Fuseki

**Testez maintenant** : http://127.0.0.1:8000/test/

