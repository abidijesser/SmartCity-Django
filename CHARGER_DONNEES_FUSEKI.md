# ✅ Charger les Données dans Fuseki

## Étape 1 : Accéder à Fuseki

**Ouvrez votre navigateur :** http://localhost:3030

Vous devriez voir l'interface de gestion Fuseki.

## Étape 2 : Créer le Dataset "transport"

1. Cliquez sur **"manage datasets"** (ou "Add dataset")
2. Dans "Dataset name", entrez : `transport`
3. Cliquez sur **"Create dataset"** ou "Add new dataset"

✅ Dataset créé !

## Étape 3 : Charger les Données

### Option A : Via Upload (Facile)

1. Dans l'interface Fuseki, sélectionnez le dataset `transport`
2. Allez dans l'onglet **"Upload"** (ou "Data" puis "Upload")
3. Cliquez sur **"Choose File"** ou **"Upload"**
4. Sélectionnez le fichier `donnees_test.rdf`
5. Cliquez sur **"Upload"** ou **"Send"**

✅ Données chargées !

### Option B : Via SPARQL INSERT (Avancé)

1. Allez sur http://localhost:3030/fuseki
2. Sélectionnez le dataset `transport`
3. Cliquez sur **"Query"**
4. Ouvrez le fichier `insert_donnees_test.sparql`
5. Copiez tout le contenu et collez-le dans l'éditeur
6. Cliquez sur **"Run Query"**

✅ Données ajoutées !

## Étape 4 : Vérifier les Données

1. Dans Fuseki, sélectionnez `transport`
2. Allez dans **"Query"**
3. Exécutez cette requête :

```sparql
SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 10
```

Vous devriez voir les triples chargés !

## Étape 5 : Tester avec Django

```powershell
python test_sparql.py
```

Ou redémarrez votre serveur Django et accédez au dashboard !

🎉 **Les données RDF s'afficheront dans vos dashboards !**

---

## 📋 Résumé

✅ Fuseki démarré : http://localhost:3030  
✅ Dataset créé : `transport`  
✅ Données chargées : `donnees_test.rdf`  
✅ Application Django : Montre les données RDF  

