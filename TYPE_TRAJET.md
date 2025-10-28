# 🛣️ TYPE DE TRAJET - Documentation

## 📋 Vue d'ensemble

Ajout du champ **"Type de trajet"** au formulaire de création de trajet avec 3 options:
- **TrajetCourt** - Trajet court (< 50 km)
- **TrajetLong** - Trajet long (> 50 km)
- **TrajetTouristique** - Trajet touristique (sites d'intérêt)

---

## 🔧 Modifications Effectuées

### **1. Formulaire - `forms.py`**

#### Nouvelle classe `TrajetForm`:
```python
class TrajetForm(forms.Form):
    """Formulaire pour créer un trajet"""
    
    TYPE_TRAJET_CHOICES = [
        ('TrajetCourt', 'Trajet Court'),
        ('TrajetLong', 'Trajet Long'),
        ('TrajetTouristique', 'Trajet Touristique'),
    ]
    
    type_trajet = forms.ChoiceField(
        required=True,
        choices=TYPE_TRAJET_CHOICES,
        label="Type de trajet",
        initial='TrajetCourt',
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-3 text-gray-900 focus:border-brand-500 focus:ring-brand-500'
        })
    )
```

---

### **2. SPARQL - `sparql_utils.py`**

#### Méthode `addTrajet()` modifiée:
```python
def addTrajet(self, depart_station_uri: str, arrivee_station_uri: str, 
              vehicule_uri: str = None, horaire_uri: str = None,
              heure_depart: str = None, heure_arrivee: str = None, 
              distance: float = None, duree: float = None, 
              nom_trajet: str = None, conducteur_uri: str = None,
              type_trajet: str = "TrajetCourt") -> bool:  # ← NOUVEAU PARAMÈTRE
```

#### Requête SPARQL générée:
```sparql
INSERT DATA {
    <Trajet_123> rdf:type transport:Trajet ;
                 rdf:type transport:TrajetCourt ;  # ← NOUVEAU TYPE
                 transport:aPourDepart <Station_1> ;
                 transport:aPourArrivee <Station_2> .
}
```

**Le trajet a maintenant 2 types:**
1. `transport:Trajet` (classe de base)
2. `transport:TrajetCourt` / `TrajetLong` / `TrajetTouristique` (sous-classe)

---

### **3. View - `views.py`**

#### `trajet_create_view()` modifiée:
```python
# Récupérer le type de trajet
type_trajet = request.POST.get('type_trajet', 'TrajetCourt')

# Passer à addTrajet
success = sparql.addTrajet(
    depart_station_uri=depart_station_uri,
    arrivee_station_uri=arrivee_station_uri,
    vehicule_uri=vehicule_uri,
    horaire_uri=horaire_uri,
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    distance=distance,
    duree=duree,
    nom_trajet=nom_trajet,
    conducteur_uri=conducteur_uri,
    type_trajet=type_trajet  # ← NOUVEAU
)
```

---

### **4. Template - `trajet_form.html`**

#### Nouveau champ ajouté:
```html
<!-- Type de Trajet -->
<div>
    <label for="type_trajet" class="block text-sm font-medium text-gray-700 mb-2">
        <i class="fas fa-route mr-1 text-brand-600"></i>
        Type de trajet <span class="text-red-500">*</span>
    </label>
    <select name="type_trajet" id="type_trajet" required
            class="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-brand-500 focus:ring-brand-500">
        <option value="TrajetCourt">Trajet Court</option>
        <option value="TrajetLong">Trajet Long</option>
        <option value="TrajetTouristique">Trajet Touristique</option>
    </select>
    <p class="mt-1 text-sm text-gray-500">
        <i class="fas fa-info-circle mr-1"></i>
        Court: &lt;50km | Long: &gt;50km | Touristique: sites d'intérêt
    </p>
</div>
```

**Position:** Entre "Station d'arrivée" et "Véhicule"

---

## 🎨 Aperçu du Formulaire

```
┌─────────────────────────────────────────────────────┐
│ 🚗 Créer un Trajet                                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Nom du trajet (optionnel)                          │
│ [_________________________________]                 │
│                                                     │
│ Station de départ *                                │
│ [gare tunis ▼]                                     │
│                                                     │
│ Station d'arrivée *                                │
│ [gare ariana ▼]                                    │
│                                                     │
│ 🛣️ Type de trajet *                                │
│ [Trajet Court ▼]                                   │
│   - Trajet Court                                   │
│   - Trajet Long                                    │
│   - Trajet Touristique                             │
│ ℹ️ Court: <50km | Long: >50km | Touristique       │
│                                                     │
│ Véhicule (optionnel)                               │
│ [bus 1 ▼]                                          │
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

### **Avant:**
```sparql
<Trajet_123> rdf:type transport:Trajet ;
             transport:aPourDepart <Station_1> ;
             transport:aPourArrivee <Station_2> .
```

### **Après:**
```sparql
<Trajet_123> rdf:type transport:Trajet ;
             rdf:type transport:TrajetCourt ;  # ← NOUVEAU
             transport:aPourDepart <Station_1> ;
             transport:aPourArrivee <Station_2> .
```

---

## 🎯 Utilisation

### **Créer un Trajet Court:**
```
Login: driver / mdp
Dashboard → Mes Trajets → Créer un trajet

Formulaire:
├── Départ: gare tunis
├── Arrivée: gare ariana
├── Type: Trajet Court  ← SÉLECTIONNER
├── Véhicule: bus 1
├── Horaire: [Bus] 08:00 → 09:30
├── Distance: 15 km
└── Créer ✅

Résultat SPARQL:
<Trajet_xxx> rdf:type transport:Trajet ;
             rdf:type transport:TrajetCourt ;
             ...
```

### **Créer un Trajet Touristique:**
```
Formulaire:
├── Départ: gare tunis
├── Arrivée: gare carthage
├── Type: Trajet Touristique  ← SÉLECTIONNER
├── Distance: 20 km
└── Créer ✅

Résultat SPARQL:
<Trajet_yyy> rdf:type transport:Trajet ;
             rdf:type transport:TrajetTouristique ;
             ...
```

---

## 🔍 Requêtes SPARQL Utiles

### **Lister tous les trajets courts:**
```sparql
SELECT ?trajet ?depart ?arrivee
WHERE {
    ?trajet rdf:type transport:TrajetCourt ;
            transport:aPourDepart ?departStation ;
            transport:aPourArrivee ?arriveeStation .
    ?departStation transport:nom ?depart .
    ?arriveeStation transport:nom ?arrivee .
}
```

### **Lister tous les trajets touristiques:**
```sparql
SELECT ?trajet ?depart ?arrivee
WHERE {
    ?trajet rdf:type transport:TrajetTouristique ;
            transport:aPourDepart ?departStation ;
            transport:aPourArrivee ?arriveeStation .
    ?departStation transport:nom ?depart .
    ?arriveeStation transport:nom ?arrivee .
}
```

### **Compter par type:**
```sparql
SELECT ?type (COUNT(?trajet) AS ?count)
WHERE {
    ?trajet rdf:type transport:Trajet ;
            rdf:type ?type .
    FILTER (?type IN (transport:TrajetCourt, transport:TrajetLong, transport:TrajetTouristique))
}
GROUP BY ?type
```

---

## 📈 Statistiques Possibles

Avec ce système, vous pouvez maintenant:

1. **Filtrer les trajets par type** dans les recherches
2. **Afficher des statistiques** par type de trajet
3. **Appliquer des règles métier** différentes selon le type:
   - Prix différent pour trajets longs
   - Réductions pour trajets touristiques
   - Priorité pour trajets courts

---

## 🎯 Exemple Complet

### **Scénario:**
```
1. Gestionnaire crée horaires
   ✅ [Bus] 08:00 → 09:30

2. Conducteur crée 3 trajets:
   
   Trajet 1 - Court:
   ├── tunis → ariana
   ├── Type: TrajetCourt
   ├── Distance: 15 km
   └── Horaire: [Bus] 08:00 → 09:30
   
   Trajet 2 - Long:
   ├── tunis → sfax
   ├── Type: TrajetLong
   ├── Distance: 270 km
   └── Horaire: manuel
   
   Trajet 3 - Touristique:
   ├── tunis → carthage
   ├── Type: TrajetTouristique
   ├── Distance: 20 km
   └── Horaire: [Bus] 08:00 → 09:30

3. Passager recherche:
   - Peut filtrer par type (futur)
   - Voit les trajets avec leur type
```

---

## ✅ Avantages

1. **Classification claire** des trajets
2. **Requêtes SPARQL** plus précises
3. **Statistiques** par type de trajet
4. **Règles métier** différenciées
5. **Extensible** - facile d'ajouter de nouveaux types

---

## 🚀 PRÊT À TESTER!

**Le champ "Type de trajet" est maintenant disponible dans le formulaire!** 🎉

### **Test:**
```
1. Login: driver / mdp
2. Dashboard → Mes Trajets → Créer un trajet
3. Voir le nouveau champ "Type de trajet"
4. Sélectionner: Trajet Court / Long / Touristique
5. Remplir le reste
6. Créer → Succès! ✅
```
