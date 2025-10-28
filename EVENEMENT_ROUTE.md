# 🛣️ ÉVÉNEMENT SUR ROUTE - Documentation

## 📋 Vue d'ensemble

Ajout d'un champ **"Route"** au formulaire d'événement pour permettre de lier un événement à une route spécifique déjà créée par le gestionnaire.

---

## 🔧 Modifications Effectuées

### **1. Formulaire - `forms.py`**

#### Nouveau champ ajouté:
```python
route = forms.CharField(
    required=False,
    label="Route",
    widget=forms.Select(attrs={
        'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
    })
)
```

**Caractéristiques:**
- Optionnel (pas obligatoire)
- Widget Select (liste déroulante)
- Rempli dynamiquement depuis la view

---

### **2. SPARQL - `sparql_utils.py`**

#### Méthode `create_evenement()` modifiée:
```python
def create_evenement(self, type_evt: str = "ÉvénementTrafic",
                     dateEvenement: str = None, 
                     description: str = None, latitude: float = None, 
                     longitude: float = None, route_uri: str = None) -> bool:  # ← NOUVEAU
```

#### Requête SPARQL générée:
```sparql
INSERT DATA {
    <Evenement_xxx> rdf:type transport:ÉvénementTrafic ;
                    rdf:type transport:Accident ;
                    transport:typeEvenement "Accident" ;
                    transport:surRoute <Route_A1> .  # ← NOUVEAU LIEN
}
```

**Propriété ajoutée:** `transport:surRoute <Route_xxx>`

---

### **3. View - `views.py`**

#### `evenement_create_view()` modifiée:
```python
# Récupérer la route
route_uri = form.cleaned_data.get('route') or None

# Charger les routes pour le formulaire
routes = []
if FUSEKI_AVAILABLE:
    try:
        routes = sparql.get_routes()
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement des routes: {str(e)}')

# Passer à create_evenement
success = sparql.create_evenement(
    type_evt=form.cleaned_data['type_evt'],
    dateEvenement=date_evt.isoformat() if date_evt else None,
    description=form.cleaned_data.get('description', ''),
    latitude=form.cleaned_data.get('latitude'),
    longitude=form.cleaned_data.get('longitude'),
    route_uri=route_uri  # ← NOUVEAU
)

# Context
return render(request, 'accounts/evenement_form.html', {
    'form': form,
    'routes': routes,  # ← NOUVEAU
    ...
})
```

---

### **4. Template - `evenement_form.html`**

#### Nouveau champ ajouté:
```html
<div>
    <label for="route" class="mb-2 block text-sm font-medium text-gray-900">
        <i class="fas fa-road mr-2 text-brand-600"></i>
        Route <span class="text-gray-400">(optionnel)</span>
    </label>
    <select name="route" id="route"
            class="w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500">
        <option value="">-- Sélectionnez une route --</option>
        {% for route in routes %}
        <option value="{{ route.route }}">
            {{ route.nom }}
            {% if route.longueur %} - {{ route.longueur }} km{% endif %}
            {% if route.etatRoute %} ({{ route.etatRoute }}){% endif %}
        </option>
        {% endfor %}
    </select>
    <p class="mt-1 text-xs text-gray-500">Route concernée par l'événement</p>
</div>
```

**Position:** Entre "Type d'événement" et "Date et heure"

---

## 🎨 Nouveau Formulaire

```
┌─────────────────────────────────────────────────────┐
│ 🚨 Créer un événement                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 🚨 Type d'événement *                              │
│ [Accident ▼]                                       │
│                                                     │
│ 🛣️ Route (optionnel)                               │
│ [Route A1 - 15 km (Bon état) ▼]  ← NOUVEAU        │
│   - Route A1 - 15 km (Bon état)                   │
│   - Route B2 - 25 km (Moyen)                      │
│   - Route Touristique - 30 km (Excellent)         │
│ Route concernée par l'événement                    │
│                                                     │
│ Date et heure de l'événement (optionnel)           │
│ [2025-10-28T23:30]                                 │
│                                                     │
│ Description (optionnel)                            │
│ [Accident sur l'autoroute A1_____________]         │
│                                                     │
│ Latitude │ Longitude                               │
│ [36.806] │ [10.181]                                │
│                                                     │
│ [Annuler]              [💾 Créer l'événement]     │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Modèle de Données

### **Événement avec Route:**
```sparql
<Evenement_abc> rdf:type transport:ÉvénementTrafic ;
                rdf:type transport:Accident ;
                transport:typeEvenement "Accident" ;
                transport:surRoute <Route_A1> ;  # ← NOUVEAU LIEN
                transport:dateEvenement "2025-10-28T23:30:00" ;
                transport:description "Accident sur l'autoroute A1" ;
                transport:latitude "36.8065"^^xsd:float ;
                transport:longitude "10.1815"^^xsd:float .
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

### **2. Utilisateur crée un Événement sur Route:**
```
Login: ahmed / mdp (ou tout utilisateur)
Dashboard → Événements → Créer un événement

Formulaire:
├── Type: Accident
├── Route: Route A1 - 15.5 km (Bon état)  ← SÉLECTIONNER
├── Date: 2025-10-28T23:30
├── Description: Accident sur l'autoroute A1
├── Latitude: 36.8065
├── Longitude: 10.1815
└── Créer l'événement ✅

Résultat SPARQL:
<Evenement_xxx> rdf:type transport:ÉvénementTrafic ;
                rdf:type transport:Accident ;
                transport:typeEvenement "Accident" ;
                transport:surRoute <Route_A1> ;  ← LIEN CRÉÉ
                transport:dateEvenement "2025-10-28T23:30:00" ;
                transport:description "Accident sur l'autoroute A1" ;
                transport:latitude "36.8065"^^xsd:float ;
                transport:longitude "10.1815"^^xsd:float .
```

---

### **3. Affichage de l'Événement:**
```
Dashboard → Événements

Liste:
┌────────────────────────────────────────────────────┐
│ 🚨 Accident                                        │
│ 🛣️ Route: Route A1 (15.5 km)  ← AFFICHÉ          │
│ 📅 Date: 2025-10-28 23:30                         │
│ 📝 Accident sur l'autoroute A1                    │
│ 📍 36.8065, 10.1815                               │
└────────────────────────────────────────────────────┘
```

---

## 🔍 Requêtes SPARQL Utiles

### **Lister tous les événements avec leur route:**
```sparql
SELECT ?evenement ?typeEvenement ?routeNom ?dateEvenement
WHERE {
    ?evenement rdf:type transport:ÉvénementTrafic ;
               transport:typeEvenement ?typeEvenement ;
               transport:surRoute ?route .
    
    ?route transport:nom ?routeNom .
    OPTIONAL { ?evenement transport:dateEvenement ?dateEvenement }
}
ORDER BY DESC(?dateEvenement)
```

### **Trouver tous les événements sur une route spécifique:**
```sparql
SELECT ?evenement ?typeEvenement ?dateEvenement ?description
WHERE {
    ?evenement transport:surRoute <Route_A1> ;
               transport:typeEvenement ?typeEvenement .
    
    OPTIONAL { ?evenement transport:dateEvenement ?dateEvenement }
    OPTIONAL { ?evenement transport:description ?description }
}
ORDER BY DESC(?dateEvenement)
```

### **Statistiques d'événements par route:**
```sparql
SELECT ?routeNom (COUNT(?evenement) AS ?nombreEvenements)
WHERE {
    ?evenement transport:surRoute ?route .
    ?route transport:nom ?routeNom .
}
GROUP BY ?routeNom
ORDER BY DESC(?nombreEvenements)
```

### **Routes avec le plus d'accidents:**
```sparql
SELECT ?routeNom (COUNT(?evenement) AS ?nombreAccidents)
WHERE {
    ?evenement rdf:type transport:Accident ;
               transport:surRoute ?route .
    ?route transport:nom ?routeNom .
}
GROUP BY ?routeNom
ORDER BY DESC(?nombreAccidents)
```

---

## 📈 Cas d'Usage

### **1. Gestion du Trafic**
```
Événement: Travaux sur Route A1
→ Alerte automatique aux conducteurs
→ Suggestion de routes alternatives
```

### **2. Statistiques**
```
Route A1:
├── 5 accidents ce mois
├── 2 travaux en cours
└── 1 manifestation prévue
→ Route à surveiller
```

### **3. Planification**
```
Événement: Manifestation sur Route B2
Date: 2025-11-01
→ Bloquer les trajets sur cette route
→ Proposer itinéraires alternatifs
```

---

## ✅ Avantages

### **1. Localisation Précise**
- ✅ Événement lié à une route spécifique
- ✅ Pas seulement des coordonnées GPS
- ✅ Contexte routier clair

### **2. Alertes Ciblées**
- ✅ Alerter uniquement les conducteurs sur cette route
- ✅ Proposer alternatives automatiquement
- ✅ Gestion proactive du trafic

### **3. Statistiques Utiles**
- ✅ Routes les plus accidentées
- ✅ Fréquence des événements par route
- ✅ Planification de maintenance

### **4. Intégration**
- ✅ Compatible avec système de trajets
- ✅ Routes déjà utilisées pour les trajets
- ✅ Données cohérentes

---

## 🧪 Scénario de Test Complet

### **Étape 1: Gestionnaire crée routes**
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

Logout
```

---

### **Étape 2: Utilisateur crée événements**
```
Login: ahmed / mdp

Événement 1:
├── Type: Accident
├── Route: Route A1 - 15 km (Bon état)  ← SÉLECTIONNER
├── Date: 2025-10-28T23:30
├── Description: Accident sur l'autoroute A1
└── Créer ✅

Événement 2:
├── Type: Travaux
├── Route: Route B2 - 25 km (Moyen)  ← SÉLECTIONNER
├── Date: 2025-11-01T08:00
├── Description: Réfection de la chaussée
└── Créer ✅

Événement 3:
├── Type: Manifestation
├── Route: (vide - pas de route spécifique)
├── Date: 2025-11-05T14:00
├── Description: Manifestation centre-ville
└── Créer ✅
```

---

### **Étape 3: Vérifier les événements**
```
Dashboard → Événements

Liste:
┌────────────────────────────────────────────────────┐
│ 🚨 Accident                                        │
│ 🛣️ Route A1 (15 km)                               │
│ 📅 2025-10-28 23:30                               │
├────────────────────────────────────────────────────┤
│ 🚧 Travaux                                         │
│ 🛣️ Route B2 (25 km)                               │
│ 📅 2025-11-01 08:00                               │
├────────────────────────────────────────────────────┤
│ 📢 Manifestation                                   │
│ 🛣️ (Aucune route)                                 │
│ 📅 2025-11-05 14:00                               │
└────────────────────────────────────────────────────┘
```

---

## ✅ Résumé

### **Modifications:**
1. ✅ Ajouté champ `route` au formulaire
2. ✅ Ajouté paramètre `route_uri` à `create_evenement()`
3. ✅ Propriété SPARQL `transport:surRoute`
4. ✅ Chargement dynamique des routes dans la view
5. ✅ Template avec liste déroulante des routes

### **Résultat:**
- ✅ Événements liés à des routes spécifiques
- ✅ Meilleure localisation des incidents
- ✅ Statistiques par route possibles
- ✅ Alertes ciblées par route

---

## 🚀 PRÊT À UTILISER!

**Les événements peuvent maintenant être liés à des routes!** 🎉

### **Test:**
```
1. Login: manager / mdp
2. Créer une route (Route A1)
3. Logout

4. Login: ahmed / mdp
5. Créer un événement
6. Voir le champ "Route" avec Route A1
7. Sélectionner Route A1
8. Créer → Succès! ✅
```
