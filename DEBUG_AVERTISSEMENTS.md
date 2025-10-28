# 🔍 DEBUG AVERTISSEMENTS - Guide de Vérification

## ✅ Modifications Effectuées

### **1. Requête SPARQL - `search_trajets_disponibles()`**
- ✅ Ajouté `?route ?routeNom` dans le SELECT
- ✅ Ajouté section OPTIONAL pour récupérer la route

### **2. Logs de Debug - `search_trajets_view()`**
- ✅ Ajouté `print()` pour voir les routes et événements
- ✅ Permet de diagnostiquer le problème

---

## 🧪 Étapes de Test

### **Étape 1: Vérifier que le trajet a une route**

1. **Ouvrir Fuseki:**
   - http://localhost:3030
   - Dataset: `transport`
   - Query

2. **Requête pour voir les trajets avec routes:**
```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>

SELECT ?trajet ?departNom ?arriveeNom ?routeNom
WHERE {
    ?trajet rdf:type transport:Trajet ;
            transport:aPourDepart ?depart ;
            transport:aPourArrivee ?arrivee .
    
    ?depart transport:nom ?departNom .
    ?arrivee transport:nom ?arriveeNom .
    
    OPTIONAL {
        ?trajet transport:utiliseRoute ?route .
        ?route transport:nom ?routeNom
    }
}
```

**Résultat attendu:**
```
trajet                  | departNom  | arriveeNom | routeNom
------------------------|------------|------------|----------
Trajet_xxx             | gare tunis | gare ariana| Route A1
```

✅ **Si routeNom est vide → Le trajet n'a PAS de route associée!**

---

### **Étape 2: Vérifier que la route a un événement**

```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>

SELECT ?route ?routeNom ?evenement ?typeEvenement
WHERE {
    ?route rdf:type transport:Route ;
           transport:nom ?routeNom .
    
    OPTIONAL {
        ?evenement transport:surRoute ?route ;
                   transport:typeEvenement ?typeEvenement .
    }
}
```

**Résultat attendu:**
```
route     | routeNom | evenement      | typeEvenement
----------|----------|----------------|---------------
Route_A1  | Route A1 | Evenement_xxx  | Travaux
```

✅ **Si evenement est vide → La route n'a PAS d'événement!**

---

### **Étape 3: Vérifier les logs Django**

1. **Lancer le serveur Django:**
```bash
python manage.py runserver
```

2. **Rechercher un trajet:**
   - Login: passenger / mdp
   - Rechercher trajet (tunis → ariana)

3. **Regarder la console:**
```
DEBUG - Trajet: http://.../Trajet_xxx, Route URI: http://.../Route_A1
DEBUG - Événements trouvés: 1
DEBUG - Type événement: http://.../Travaux
DEBUG - Type name extrait: Travaux
DEBUG - Warning ajouté: ⚠️ Attention : travaux signalés sur cette route. Retard possible.
```

**Diagnostic:**
- ✅ Si "Route URI: None" → Trajet n'a pas de route
- ✅ Si "Événements trouvés: 0" → Route n'a pas d'événement
- ✅ Si tout s'affiche → Le warning devrait apparaître!

---

## 🔧 Solutions aux Problèmes

### **Problème 1: Trajet n'a pas de route**

**Cause:** Le trajet a été créé sans sélectionner de route

**Solution:**
1. Login: driver / mdp
2. Dashboard → Mes Trajets
3. Supprimer le trajet existant
4. Créer nouveau trajet
5. **IMPORTANT:** Sélectionner une route dans le formulaire
6. Créer

---

### **Problème 2: Route n'a pas d'événement**

**Cause:** L'événement n'est pas lié à la route

**Solution:**
1. Login: ahmed / mdp (ou tout utilisateur)
2. Dashboard → Événements → Créer un événement
3. Type: Travaux (ou Accident, Manifestation)
4. **IMPORTANT:** Sélectionner la même route que le trajet
5. Créer

---

### **Problème 3: Propriété SPARQL incorrecte**

**Vérifier dans Fuseki:**
```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>

SELECT ?trajet ?route
WHERE {
    ?trajet transport:utiliseRoute ?route .
}
```

Si vide, vérifier:
```sparql
SELECT ?trajet ?p ?route
WHERE {
    ?trajet rdf:type transport:Trajet ;
            ?p ?route .
    ?route rdf:type transport:Route .
}
```

**Cela montrera quelle propriété est utilisée!**

---

## 📝 Scénario de Test Complet

### **1. Créer Route**
```
Login: manager / mdp
Dashboard → Routes → Créer une route

Formulaire:
├── Nom: Route Test Debug
├── Type: Route Nationale
├── Longueur: 20
├── État: Bon état
└── Créer ✅

Logout
```

---

### **2. Créer Trajet avec Route**
```
Login: driver / mdp
Dashboard → Mes Trajets → Créer un trajet

Formulaire:
├── Départ: gare tunis
├── Arrivée: gare ariana
├── Type: Trajet Court
├── Véhicule: bus 1
├── Route: Route Test Debug  ← IMPORTANT: SÉLECTIONNER
├── Horaire: [Bus] 10:00 → 12:00
├── Distance: 20
└── Créer ✅

Vérifier dans Fuseki:
SELECT ?trajet ?route WHERE {
    ?trajet transport:utiliseRoute ?route .
}

✅ Doit montrer le lien!

Logout
```

---

### **3. Créer Événement sur Route**
```
Login: ahmed / mdp
Dashboard → Événements → Créer un événement

Formulaire:
├── Type: Travaux
├── Route: Route Test Debug  ← IMPORTANT: MÊME ROUTE
├── Date: 2025-10-29T00:00
├── Description: Test debug
└── Créer ✅

Vérifier dans Fuseki:
SELECT ?evenement ?route WHERE {
    ?evenement transport:surRoute ?route .
}

✅ Doit montrer le lien!

Logout
```

---

### **4. Rechercher Trajet (Passager)**
```
Login: passenger / mdp
Dashboard → Rechercher un Trajet

Formulaire:
├── Ville départ: tunis
├── Ville arrivée: ariana
└── Rechercher 🔍

Regarder la console Django:
DEBUG - Trajet: ..., Route URI: ...Route_Test_Debug
DEBUG - Événements trouvés: 1
DEBUG - Type événement: ...Travaux
DEBUG - Type name extrait: Travaux
DEBUG - Warning ajouté: ⚠️ Attention : travaux signalés...

Regarder la page web:
┌────────────────────────────────────────────┐
│ gare tunis → gare ariana                  │
│ ...                                        │
│ ⚠️ Attention : travaux signalés sur      │
│    cette route. Retard possible.          │
└────────────────────────────────────────────┘

✅ L'avertissement doit s'afficher!
```

---

## 🔍 Requêtes SPARQL de Diagnostic

### **Tout vérifier en une requête:**
```sparql
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>

SELECT ?trajet ?departNom ?arriveeNom ?routeNom ?evenementType
WHERE {
    ?trajet rdf:type transport:Trajet ;
            transport:aPourDepart ?depart ;
            transport:aPourArrivee ?arrivee .
    
    ?depart transport:nom ?departNom .
    ?arrivee transport:nom ?arriveeNom .
    
    OPTIONAL {
        ?trajet transport:utiliseRoute ?route .
        ?route transport:nom ?routeNom .
        
        OPTIONAL {
            ?evenement transport:surRoute ?route ;
                       transport:typeEvenement ?evenementType .
        }
    }
}
```

**Résultat attendu pour que ça marche:**
```
trajet      | departNom  | arriveeNom | routeNom | evenementType
------------|------------|------------|----------|---------------
Trajet_xxx  | gare tunis | gare ariana| Route A1 | Travaux
```

**Si une colonne est vide:**
- `routeNom` vide → Trajet n'a pas de route
- `evenementType` vide → Route n'a pas d'événement

---

## ✅ Checklist de Vérification

- [ ] Route créée par gestionnaire
- [ ] Trajet créé avec route sélectionnée
- [ ] Événement créé avec route sélectionnée
- [ ] Requête SPARQL montre le lien trajet→route
- [ ] Requête SPARQL montre le lien événement→route
- [ ] Logs Django affichent les informations
- [ ] Avertissement s'affiche sur la page web

---

## 🚀 Si Tout Est Correct

**Supprimer les logs de debug:**

Dans `views.py`, supprimer les lignes:
```python
print(f"DEBUG - Trajet: ...")  # À SUPPRIMER
print(f"DEBUG - Événements trouvés: ...")  # À SUPPRIMER
print(f"DEBUG - Type événement: ...")  # À SUPPRIMER
print(f"DEBUG - Type name extrait: ...")  # À SUPPRIMER
print(f"DEBUG - Warning ajouté: ...")  # À SUPPRIMER
```

---

## 📞 Besoin d'Aide?

**Partagez:**
1. Résultat de la requête SPARQL "Tout vérifier"
2. Logs de la console Django
3. Capture d'écran de la page de recherche

**Cela permettra de diagnostiquer le problème!**
