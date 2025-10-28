# 🛣️ SÉLECTION DE ROUTE - Documentation

## 📋 Vue d'ensemble

Le conducteur peut maintenant **sélectionner une Route existante** lors de la création d'un trajet. Les routes sont créées par le gestionnaire via le CRUD Route.

---

## 🔧 Modifications Effectuées

### **1. SPARQL - `sparql_utils.py`**

#### ✅ Méthode `addTrajet()` modifiée:
```python
def addTrajet(self, depart_station_uri: str, arrivee_station_uri: str, 
              vehicule_uri: str = None, horaire_uri: str = None,
              route_uri: str = None,  # ← NOUVEAU PARAMÈTRE
              heure_depart: str = None, heure_arrivee: str = None, 
              distance: float = None, duree: float = None, 
              nom_trajet: str = None, conducteur_uri: str = None,
              type_trajet: str = "TrajetCourt") -> bool:
```

#### Requête SPARQL générée:
```sparql
INSERT DATA {
    <Trajet_123> rdf:type transport:Trajet ;
                 rdf:type transport:TrajetCourt ;
                 transport:aPourDepart <Station_1> ;
                 transport:aPourArrivee <Station_2> ;
                 transport:utiliseRoute <Route_A1> .  # ← NOUVEAU LIEN
}
```

**Propriété ajoutée:** `transport:utiliseRoute`

---

#### ✅ Méthode `get_all_trajets()` modifiée:
```sparql
SELECT ?trajet ?heureDepart ?heureArrivee ?dureeTrajet ?distanceTrajet 
       ?departStation ?departNom ?arriveeStation ?arriveeNom 
       ?vehicule ?vehiculeNom ?horaire ?horaireTypeVehicule
       ?route ?routeNom  # ← NOUVEAU
WHERE {
    ?trajet rdf:type transport:Trajet .
    
    # ... autres propriétés ...
    
    # Route (si lié à une route)
    OPTIONAL {
        ?trajet transport:utiliseRoute ?route .
        ?route transport:nom ?routeNom
    }
}
```

**Récupère:** Nom de la route si le trajet en utilise une

---

### **2. View - `views.py`**

#### ✅ `trajet_create_view()` modifiée:
```python
# Récupérer la route
route_uri = request.POST.get('route') or None

# Charger les routes
routes = sparql.get_routes()

# Passer à addTrajet
success = sparql.addTrajet(
    depart_station_uri=depart_station_uri,
    arrivee_station_uri=arrivee_station_uri,
    vehicule_uri=vehicule_uri,
    horaire_uri=horaire_uri,
    route_uri=route_uri,  # ← NOUVEAU
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    distance=distance,
    duree=duree,
    nom_trajet=nom_trajet,
    conducteur_uri=conducteur_uri,
    type_trajet=type_trajet
)

# Context
return render(request, 'accounts/trajet_form.html', {
    'stations': stations,
    'vehicules': vehicules,
    'horaires': horaires,
    'routes': routes,  # ← NOUVEAU
    ...
})
```

---

### **3. Template - `trajet_form.html`**

#### Nouveau champ ajouté:
```html
<!-- Route (créée par le gestionnaire) -->
<div>
    <label for="route" class="block text-sm font-medium text-gray-700 mb-2">
        <i class="fas fa-road mr-1 text-brand-600"></i>
        Route <span class="text-gray-400">(optionnel)</span>
    </label>
    <select name="route" id="route"
            class="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-brand-500 focus:ring-brand-500">
        <option value="">-- Sélectionnez une route --</option>
        {% for route in routes %}
        <option value="{{ route.route }}">
            {{ route.nom }}
            {% if route.longueur %} - {{ route.longueur }} km{% endif %}
            {% if route.etatRoute %} ({{ route.etatRoute }}){% endif %}
        </option>
        {% endfor %}
    </select>
    <p class="mt-1 text-sm text-gray-500">
        <i class="fas fa-info-circle mr-1"></i>
        Route pré-définie par le gestionnaire
    </p>
</div>
```

**Position:** Entre "Véhicule" et "Horaire"

---

## 🎨 Aperçu du Formulaire

```
┌─────────────────────────────────────────────────────┐
│ 🚗 Créer un Trajet                                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Station de départ *                                │
│ [gare tunis ▼]                                     │
│                                                     │
│ Station d'arrivée *                                │
│ [gare ariana ▼]                                    │
│                                                     │
│ 🛣️ Type de trajet *                                │
│ [Trajet Court ▼]                                   │
│                                                     │
│ Véhicule (optionnel)                               │
│ [bus 1 ▼]                                          │
│                                                     │
│ 🛣️ Route (optionnel)                               │
│ [Route A1 - 15 km (Bon état) ▼]  ← NOUVEAU        │
│ ℹ️ Route pré-définie par le gestionnaire          │
│                                                     │
│ 🕐 Horaire (recommandé)                            │
│ [[🚌 Bus] 08:00 → 09:30 (Lundi) ▼]                │
│                                                     │
│ ... (autres champs)                                │
│                                                     │
│ [Annuler]                    [💾 Créer]           │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Modèle de Données

### **Trajet avec Route:**
```sparql
<Trajet_123> rdf:type transport:Trajet ;
             rdf:type transport:TrajetCourt ;
             transport:aPourDepart <Station_tunis> ;
             transport:aPourArrivee <Station_ariana> ;
             transport:utiliseVehicule <Vehicule_bus1> ;
             transport:utiliseRoute <Route_A1> ;  # ← NOUVEAU
             transport:aHoraire <Horaire_1> ;
             transport:conduitPar <User_driver> .
```

### **Route (créée par Gestionnaire):**
```sparql
<Route_A1> rdf:type transport:Route ;
           rdf:type transport:RouteNationale ;
           transport:nom "Route A1" ;
           transport:longueur "15.5"^^xsd:float ;
           transport:etatRoute "Bon état" .
```

---

## 🎯 Flux Complet

### **1. Gestionnaire crée une Route:**
```
Login: manager / mdp
Dashboard → Routes → Créer une route

Formulaire:
├── Nom: Route A1
├── Type: Route Nationale
├── Longueur: 15.5 km
├── État: Bon état
└── Créer ✅

Résultat SPARQL:
<Route_A1> rdf:type transport:Route ;
           rdf:type transport:RouteNationale ;
           transport:nom "Route A1" ;
           transport:longueur "15.5"^^xsd:float ;
           transport:etatRoute "Bon état" .
```

---

### **2. Conducteur crée un Trajet avec Route:**
```
Login: driver / mdp
Dashboard → Mes Trajets → Créer un trajet

Formulaire:
├── Départ: gare tunis
├── Arrivée: gare ariana
├── Type: Trajet Court
├── Véhicule: bus 1
├── Route: Route A1 - 15.5 km (Bon état)  ← SÉLECTIONNER
├── Horaire: [Bus] 08:00 → 09:30
├── Distance: 15
└── Créer ✅

Résultat SPARQL:
<Trajet_xxx> rdf:type transport:Trajet ;
             rdf:type transport:TrajetCourt ;
             transport:aPourDepart <Station_tunis> ;
             transport:aPourArrivee <Station_ariana> ;
             transport:utiliseVehicule <Vehicule_bus1> ;
             transport:utiliseRoute <Route_A1> ;  ← LIEN CRÉÉ
             transport:aHoraire <Horaire_1> ;
             transport:conduitPar <User_driver> .
```

---

### **3. Affichage du Trajet:**
```
Dashboard → Mes Trajets

Liste:
┌────────────────────────────────────────────────────┐
│ gare tunis → gare ariana                          │
│ 🚌 bus 1                                          │
│ 🛣️ Route: Route A1 (15.5 km)  ← AFFICHÉ          │
│ Départ: 08:00 │ Arrivée: 09:30                   │
│ Distance: 15 km                                   │
└────────────────────────────────────────────────────┘
```

---

## 🔍 Requêtes SPARQL Utiles

### **Lister tous les trajets avec leur route:**
```sparql
SELECT ?trajet ?depart ?arrivee ?routeNom ?routeLongueur
WHERE {
    ?trajet rdf:type transport:Trajet ;
            transport:aPourDepart ?departStation ;
            transport:aPourArrivee ?arriveeStation ;
            transport:utiliseRoute ?route .
    
    ?departStation transport:nom ?depart .
    ?arriveeStation transport:nom ?arrivee .
    ?route transport:nom ?routeNom .
    OPTIONAL { ?route transport:longueur ?routeLongueur }
}
```

### **Trouver tous les trajets utilisant une route spécifique:**
```sparql
SELECT ?trajet ?depart ?arrivee ?conducteur
WHERE {
    ?trajet transport:utiliseRoute <Route_A1> ;
            transport:aPourDepart ?departStation ;
            transport:aPourArrivee ?arriveeStation ;
            transport:conduitPar ?conducteur .
    
    ?departStation transport:nom ?depart .
    ?arriveeStation transport:nom ?arrivee .
}
```

### **Statistiques par route:**
```sparql
SELECT ?routeNom (COUNT(?trajet) AS ?nombreTrajets)
WHERE {
    ?trajet transport:utiliseRoute ?route .
    ?route transport:nom ?routeNom .
}
GROUP BY ?routeNom
ORDER BY DESC(?nombreTrajets)
```

---

## 📈 Avantages

### **1. Centralisation**
- Routes gérées par le gestionnaire
- Informations cohérentes (longueur, état)
- Mise à jour centralisée

### **2. Traçabilité**
- Savoir quels trajets utilisent quelle route
- Statistiques d'utilisation des routes
- Planification de maintenance

### **3. Informations Enrichies**
- État de la route (Bon/Moyen/Mauvais)
- Longueur exacte
- Type de route (Nationale/Départementale/etc.)

### **4. Flexibilité**
- Route optionnelle (pas obligatoire)
- Compatible avec trajets existants
- Évolutif (ajout de nouvelles propriétés)

---

## 🧪 Scénario de Test Complet

### **Étape 1: Gestionnaire crée 3 routes**
```
Login: manager / mdp

Route 1:
├── Nom: Route A1
├── Type: Route Nationale
├── Longueur: 15 km
└── État: Bon état

Route 2:
├── Nom: Route B2
├── Type: Route Départementale
├── Longueur: 25 km
└── État: Moyen

Route 3:
├── Nom: Route Touristique
├── Type: Route Touristique
├── Longueur: 30 km
└── État: Excellent

Logout
```

---

### **Étape 2: Conducteur crée trajets avec routes**
```
Login: driver / mdp

Trajet 1:
├── Départ: gare tunis
├── Arrivée: gare ariana
├── Type: Trajet Court
├── Route: Route A1 - 15 km (Bon état)  ← SÉLECTIONNER
└── Créer ✅

Trajet 2:
├── Départ: gare ariana
├── Arrivée: gare manouba
├── Type: Trajet Long
├── Route: Route B2 - 25 km (Moyen)  ← SÉLECTIONNER
└── Créer ✅

Trajet 3:
├── Départ: gare tunis
├── Arrivée: gare carthage
├── Type: Trajet Touristique
├── Route: Route Touristique - 30 km (Excellent)  ← SÉLECTIONNER
└── Créer ✅
```

---

### **Étape 3: Vérifier les trajets**
```
Dashboard → Mes Trajets

Liste:
┌────────────────────────────────────────────────────┐
│ gare tunis → gare ariana                          │
│ 🛣️ Route A1 (15 km - Bon état)                    │
├────────────────────────────────────────────────────┤
│ gare ariana → gare manouba                        │
│ 🛣️ Route B2 (25 km - Moyen)                       │
├────────────────────────────────────────────────────┤
│ gare tunis → gare carthage                        │
│ 🛣️ Route Touristique (30 km - Excellent)         │
└────────────────────────────────────────────────────┘
```

---

## ✅ Résumé

### **Modifications:**
1. ✅ `addTrajet()` - Paramètre `route_uri` ajouté
2. ✅ `get_all_trajets()` - Récupère route et nom
3. ✅ `trajet_create_view()` - Charge et passe routes
4. ✅ `trajet_form.html` - Champ sélection route

### **Propriété SPARQL:**
```sparql
transport:utiliseRoute <Route_xxx>
```

### **Résultat:**
- ✅ Conducteur sélectionne route existante
- ✅ Trajet lié à la route
- ✅ Informations route affichées
- ✅ Statistiques possibles par route

---

## 🚀 PRÊT À TESTER!

**Le conducteur peut maintenant sélectionner une route lors de la création de trajet!** 🎉

### **Test:**
```
1. Login: manager / mdp
2. Créer une route (Route A1)
3. Logout

4. Login: driver / mdp
5. Créer un trajet
6. Voir le champ "Route" avec Route A1
7. Sélectionner Route A1
8. Créer → Succès! ✅
```
