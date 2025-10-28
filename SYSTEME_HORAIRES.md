# 🕐 SYSTÈME D'HORAIRES - Documentation Complète

## 📋 Vue d'ensemble

Le système a été modifié pour que:
1. **GESTIONNAIRE** crée des horaires avec type de véhicule (Bus/Taxi/Metro)
2. **CONDUCTEUR** sélectionne un horaire existant lors de la création de trajet
3. **Compatibilité** maintenue avec l'ancien système (saisie manuelle)

---

## 🔧 Modifications Techniques

### **1. SPARQL - `sparql_utils.py`**

#### ✅ Méthode `create_horaire()` (ligne 525)
```python
def create_horaire(self, heureDepart: str, heureArrivee: str, typeVehicule: str = "Bus", 
                  jour: str = None, type_horaire: str = "Horaire") -> bool:
```

**Nouveau paramètre:**
- `typeVehicule`: "Bus", "Taxi" ou "Metro"

**Propriété SPARQL ajoutée:**
```sparql
transport:typeVehicule "Bus"
```

---

#### ✅ Méthode `get_horaires()` (ligne 507)
```sparql
SELECT ?horaire ?heureDepart ?heureArrivee ?typeVehicule ?jour ?type
WHERE {
    ?horaire rdf:type/rdfs:subClassOf* transport:Horaire .
    OPTIONAL { ?horaire transport:typeVehicule ?typeVehicule }
    ...
}
ORDER BY ?typeVehicule ?jour ?heureDepart
```

**Récupère maintenant:** Type de véhicule pour chaque horaire

---

#### ✅ Méthode `addTrajet()` (ligne 271)
```python
def addTrajet(self, depart_station_uri: str, arrivee_station_uri: str, 
              vehicule_uri: str = None, horaire_uri: str = None,
              heure_depart: str = None, heure_arrivee: str = None, ...)
```

**Nouveau paramètre:**
- `horaire_uri`: URI de l'horaire (prioritaire sur heure_depart/heure_arrivee)

**Logique:**
```python
if horaire_uri:
    # Lier le trajet à l'horaire
    insert_query += f'<{trajet_uri}> transport:aHoraire <{horaire_uri}> .\n'
else:
    # Ancien système: heures manuelles
    if heure_depart:
        insert_query += f'<{trajet_uri}> transport:heureDepart "{heure_depart}" .\n'
```

**Propriété SPARQL ajoutée:**
```sparql
transport:aHoraire <Horaire_abc123>
```

---

#### ✅ Méthode `get_all_trajets()` (ligne 340)
```sparql
SELECT ?trajet ?heureDepart ?heureArrivee ... ?horaire ?horaireTypeVehicule
WHERE {
    ?trajet rdf:type transport:Trajet .
    
    # Horaire (si lié à un horaire)
    OPTIONAL {
        ?trajet transport:aHoraire ?horaire .
        ?horaire transport:heureDepart ?heureDepart .
        ?horaire transport:heureArrivee ?heureArrivee .
        OPTIONAL { ?horaire transport:typeVehicule ?horaireTypeVehicule }
    }
    
    # Propriétés du trajet (si pas d'horaire, heures manuelles)
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee }
    ...
}
```

**Récupère:** Heures depuis l'horaire OU depuis le trajet (compatibilité)

---

### **2. FORMULAIRES - `forms.py`**

#### ✅ Classe `HoraireForm` (ligne 105)
```python
TYPE_VEHICULE_CHOICES = [
    ('Bus', 'Bus'),
    ('Taxi', 'Taxi'),
    ('Metro', 'Metro'),
]

typeVehicule = forms.ChoiceField(
    required=True,
    choices=TYPE_VEHICULE_CHOICES,
    label="Type de véhicule",
    initial='Bus',
    ...
)
```

**Nouveau champ:** Sélection du type de véhicule

---

### **3. VIEWS - `views.py`**

#### ✅ `horaire_create_view()` (ligne 764)
```python
success = sparql.create_horaire(
    heureDepart=str(form.cleaned_data['heureDepart']),
    heureArrivee=str(form.cleaned_data['heureArrivee']),
    typeVehicule=form.cleaned_data.get('typeVehicule', 'Bus'),  # ← Nouveau
    jour=form.cleaned_data.get('jour') or None,
    type_horaire=form.cleaned_data['type_horaire']
)
```

**Passe:** Type de véhicule à la création

---

#### ✅ `trajet_create_view()` (ligne 477)
```python
# Récupération
horaire_uri = request.POST.get('horaire') or None

# Passage à addTrajet
success = sparql.addTrajet(
    depart_station_uri=depart_station_uri,
    arrivee_station_uri=arrivee_station_uri,
    vehicule_uri=vehicule_uri,
    horaire_uri=horaire_uri,  # ← Nouveau
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    ...
)

# Chargement des horaires pour le formulaire
horaires = sparql.get_horaires()

# Context
return render(request, 'accounts/trajet_form.html', {
    'stations': stations,
    'vehicules': vehicules,
    'horaires': horaires,  # ← Nouveau
    ...
})
```

**Récupère et passe:** Liste des horaires au template

---

### **4. TEMPLATES**

#### ✅ `trajet_form.html`
```html
<!-- Horaire (créé par le gestionnaire) -->
<div class="col-span-2">
    <label for="horaire">
        <i class="fas fa-clock mr-1 text-brand-600"></i>
        Horaire <span class="text-gray-400">(recommandé - créé par le gestionnaire)</span>
    </label>
    <select name="horaire" id="horaire">
        <option value="">-- Sélectionnez un horaire ou saisissez manuellement ci-dessous --</option>
        {% for horaire in horaires %}
        <option value="{{ horaire.horaire }}">
            {% if horaire.typeVehicule %}[{{ horaire.typeVehicule }}]{% endif %}
            {{ horaire.heureDepart|slice:":5" }} → {{ horaire.heureArrivee|slice:":5" }}
            {% if horaire.jour %}({{ horaire.jour }}){% endif %}
        </option>
        {% endfor %}
    </select>
    <p class="mt-1 text-sm text-gray-500">
        <i class="fas fa-info-circle mr-1"></i>
        Si vous sélectionnez un horaire, les champs ci-dessous seront ignorés
    </p>
</div>

<!-- Heure de départ (manuel - si pas d'horaire) -->
<div>
    <label for="heure_depart">
        Heure de départ <span class="text-gray-400">(si pas d'horaire)</span>
    </label>
    <input type="datetime-local" name="heure_depart" id="heure_depart">
</div>
```

**Affiche:**
- Liste déroulante d'horaires avec type de véhicule
- Champs manuels en fallback

---

## 🎯 Flux Utilisateur

### **1. GESTIONNAIRE crée un horaire**

```
Login Gestionnaire → Dashboard → Horaires → Créer un horaire

Formulaire:
├── Type de véhicule: [Bus] [Taxi] [Metro]  ← NOUVEAU
├── Heure départ: 08:00
├── Heure arrivée: 09:30
├── Jour: Lundi (optionnel)
└── Type horaire: Horaire Bus

Créer → Horaire sauvegardé avec typeVehicule="Bus"
```

**SPARQL généré:**
```sparql
INSERT DATA {
    <Horaire_abc123> rdf:type transport:Horaire ;
                     rdf:type transport:HoraireBus ;
                     transport:heureDepart "08:00:00" ;
                     transport:heureArrivee "09:30:00" ;
                     transport:typeVehicule "Bus" ;
                     transport:jour "Lundi" .
}
```

---

### **2. CONDUCTEUR crée un trajet**

```
Login Conducteur → Dashboard → Mes Trajets → Créer un trajet

Formulaire:
├── Départ: tunis gare
├── Arrivée: ariana gare
├── Véhicule: bus 1
├── Horaire: [Bus] 08:00 → 09:30 (Lundi)  ← NOUVEAU (liste déroulante)
│   OU
├── Heure départ: (manuel si pas d'horaire)
├── Heure arrivée: (manuel si pas d'horaire)
├── Distance: 15
└── Durée: 2

Créer → Trajet lié à l'horaire
```

**SPARQL généré:**
```sparql
INSERT DATA {
    <Trajet_123> rdf:type transport:Trajet ;
                 transport:aPourDepart <Station_tunis> ;
                 transport:aPourArrivee <Station_ariana> ;
                 transport:utiliseVehicule <Vehicule_bus1> ;
                 transport:aHoraire <Horaire_abc123> ;  ← NOUVEAU
                 transport:distanceTrajet "15.0"^^xsd:float ;
                 transport:dureeTrajet "2.0"^^xsd:float ;
                 transport:conduitPar <User_driver> .
}
```

---

### **3. Affichage du trajet**

Quand on récupère le trajet:

```sparql
SELECT ?trajet ?heureDepart ?heureArrivee ?horaireTypeVehicule
WHERE {
    ?trajet rdf:type transport:Trajet .
    
    # Récupère heures depuis l'horaire
    OPTIONAL {
        ?trajet transport:aHoraire ?horaire .
        ?horaire transport:heureDepart ?heureDepart .
        ?horaire transport:heureArrivee ?heureArrivee .
        ?horaire transport:typeVehicule ?horaireTypeVehicule .
    }
    
    # OU depuis le trajet (ancien système)
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee }
}
```

**Résultat:**
```
heureDepart: "08:00:00"
heureArrivee: "09:30:00"
horaireTypeVehicule: "Bus"
```

---

## 📊 Modèle de Données

### **Avant (Ancien système)**
```
Trajet
├── transport:heureDepart "2025-10-28T08:00:00"
└── transport:heureArrivee "2025-10-28T09:30:00"
```

### **Après (Nouveau système)**
```
Trajet
└── transport:aHoraire → Horaire
                         ├── transport:heureDepart "08:00:00"
                         ├── transport:heureArrivee "09:30:00"
                         ├── transport:typeVehicule "Bus"
                         └── transport:jour "Lundi"
```

### **Compatibilité (Les deux fonctionnent)**
```
Trajet (ancien)
├── transport:heureDepart "2025-10-28T08:00:00"
└── transport:heureArrivee "2025-10-28T09:30:00"

Trajet (nouveau)
└── transport:aHoraire <Horaire_123>
```

---

## 🧪 Scénario de Test Complet

### **Étape 1: Gestionnaire crée des horaires**
```
Login: manager / mdp

Dashboard → Horaires → Créer

Horaire 1:
- Type véhicule: Bus
- Départ: 08:00
- Arrivée: 09:30
- Jour: Lundi
→ Créer

Horaire 2:
- Type véhicule: Taxi
- Départ: 14:00
- Arrivée: 15:00
- Jour: (tous les jours)
→ Créer

Horaire 3:
- Type véhicule: Metro
- Départ: 06:00
- Arrivée: 06:45
- Jour: (tous les jours)
→ Créer

Logout
```

---

### **Étape 2: Conducteur crée un trajet avec horaire**
```
Login: driver / mdp

Dashboard → Mes Trajets → Créer un trajet

Formulaire:
- Départ: tunis gare
- Arrivée: ariana gare
- Véhicule: bus 1
- Horaire: [Bus] 08:00 → 09:30 (Lundi)  ← Sélectionner dans la liste
- Distance: 15
- Durée: 2

Créer → Succès!

Résultat:
✅ Trajet créé avec horaire Bus
✅ Heures automatiquement récupérées de l'horaire
✅ Type véhicule: Bus
```

---

### **Étape 3: Vérifier l'affichage**
```
Dashboard → Mes Trajets

Liste:
┌────────────────────────────────────────┐
│ tunis gare → ariana gare              │
│ Départ: 08:00 (depuis horaire Bus)    │
│ Arrivée: 09:30                        │
│ Distance: 15 km                       │
│ Durée: 2 h                            │
└────────────────────────────────────────┘
```

---

### **Étape 4: Test compatibilité (ancien système)**
```
Créer un autre trajet SANS horaire:

Formulaire:
- Départ: ariana gare
- Arrivée: tunis gare
- Véhicule: bus 1
- Horaire: (vide)
- Heure départ: 2025-10-30T10:00  ← Saisie manuelle
- Heure arrivée: 2025-10-30T11:00
- Distance: 15
- Durée: 1.5

Créer → Succès!

Résultat:
✅ Trajet créé avec heures manuelles
✅ Pas d'horaire lié
✅ Ancien système fonctionne toujours
```

---

## ✅ Avantages du Nouveau Système

### **1. Centralisation**
- Horaires gérés par le gestionnaire
- Pas de duplication de données
- Modification facile (changer un horaire = tous les trajets mis à jour)

### **2. Cohérence**
- Types de véhicules standardisés (Bus/Taxi/Metro)
- Heures cohérentes entre trajets
- Moins d'erreurs de saisie

### **3. Flexibilité**
- Conducteur peut choisir horaire OU saisir manuellement
- Compatibilité avec l'ancien système
- Migration progressive possible

### **4. Évolutivité**
- Facile d'ajouter de nouveaux types de véhicules
- Possibilité d'ajouter des règles (ex: horaires de pointe)
- Base pour fonctionnalités avancées (récurrence, etc.)

---

## 🔍 Requêtes SPARQL Utiles

### **Lister tous les horaires par type de véhicule**
```sparql
SELECT ?horaire ?typeVehicule ?heureDepart ?heureArrivee
WHERE {
    ?horaire rdf:type transport:Horaire ;
             transport:typeVehicule ?typeVehicule ;
             transport:heureDepart ?heureDepart ;
             transport:heureArrivee ?heureArrivee .
}
ORDER BY ?typeVehicule ?heureDepart
```

### **Trouver tous les trajets utilisant un horaire spécifique**
```sparql
SELECT ?trajet ?depart ?arrivee
WHERE {
    ?trajet transport:aHoraire <Horaire_abc123> ;
            transport:aPourDepart ?departStation ;
            transport:aPourArrivee ?arriveeStation .
    ?departStation transport:nom ?depart .
    ?arriveeStation transport:nom ?arrivee .
}
```

### **Trajets Bus du lundi**
```sparql
SELECT ?trajet ?heureDepart
WHERE {
    ?trajet transport:aHoraire ?horaire .
    ?horaire transport:typeVehicule "Bus" ;
             transport:jour "Lundi" ;
             transport:heureDepart ?heureDepart .
}
ORDER BY ?heureDepart
```

---

## 🎉 RÉSUMÉ

✅ **Gestionnaire** crée horaires avec type véhicule (Bus/Taxi/Metro)  
✅ **Conducteur** sélectionne horaire dans liste déroulante  
✅ **Compatibilité** avec saisie manuelle maintenue  
✅ **Requêtes** SPARQL optimisées pour récupérer heures  
✅ **UI** moderne avec icônes et messages clairs  

**Prêt à tester!** 🚀
