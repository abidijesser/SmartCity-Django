# ⚠️ AVERTISSEMENTS TRAJETS - Documentation

## 📋 Vue d'ensemble

Système d'avertissement automatique pour les passagers lorsqu'un trajet utilise une route sur laquelle un événement est signalé (accident, travaux, manifestation).

---

## 🔧 Modifications Effectuées

### **1. SPARQL - `sparql_utils.py`**

#### Nouvelle méthode `get_evenements_by_route()`:
```python
def get_evenements_by_route(self, route_uri: str) -> List[Dict]:
    """Récupère tous les événements actifs sur une route spécifique"""
    query = f"""
SELECT ?evenement ?typeEvenement ?dateEvenement ?description ?type
WHERE {{
    ?evenement transport:surRoute <{route_uri}> ;
               rdf:type/rdfs:subClassOf* transport:ÉvénementTrafic .
    OPTIONAL {{ ?evenement transport:typeEvenement ?typeEvenement }}
    OPTIONAL {{ ?evenement transport:dateEvenement ?dateEvenement }}
    OPTIONAL {{ ?evenement transport:description ?description }}
    OPTIONAL {{ 
        ?evenement rdf:type ?type .
        FILTER (?type != transport:ÉvénementTrafic)
    }}
}}
ORDER BY DESC(?dateEvenement)
"""
    return self.execute_query(query)
```

**Fonction:** Récupère tous les événements liés à une route spécifique

---

### **2. View - `views.py`**

#### Modification de `search_trajets_view()`:
```python
# Ajouter les avertissements pour les trajets avec événements sur leur route
for trajet in trajets:
    route_uri = trajet.get('route')
    if route_uri:
        # Récupérer les événements sur cette route
        evenements = sparql.get_evenements_by_route(route_uri)
        if evenements:
            # Prendre le premier événement (le plus récent)
            evt = evenements[0]
            type_evt = evt.get('type', '')
            
            # Extraire le nom du type (gérer # et /)
            if type_evt:
                if '#' in type_evt:
                    type_name = type_evt.split('#')[-1]
                else:
                    type_name = type_evt.split('/')[-1]
            else:
                type_name = 'ÉvénementTrafic'
            
            # Générer le message d'avertissement selon le type
            if type_name == 'Accident':
                trajet['warning'] = "⚠️ Attention : accident signalé sur cette route. Retard possible."
            elif type_name == 'Travaux':
                trajet['warning'] = "⚠️ Attention : travaux signalés sur cette route. Retard possible."
            elif type_name == 'Manifestation':
                trajet['warning'] = "⚠️ Attention : manifestation signalée sur cette route. Retard possible."
            else:
                trajet['warning'] = "⚠️ Attention : événement signalé sur cette route. Retard possible."
```

**Logique:**
1. Pour chaque trajet trouvé
2. Si le trajet a une route associée
3. Récupérer les événements sur cette route
4. Générer un message d'avertissement selon le type d'événement
5. Ajouter le message au trajet

---

### **3. Template - `search_trajets.html`**

#### Affichage de l'avertissement:
```html
{% if trajet.warning %}
<div class="mt-3 rounded-lg border border-yellow-300 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
    {{ trajet.warning }}
</div>
{% endif %}
```

**Style:** Bandeau jaune avec bordure, icône ⚠️ et texte explicatif

---

## 🎨 Aperçu Visuel

### **Trajet SANS événement:**
```
┌────────────────────────────────────────────────────┐
│ 🟢 gare tunis → 🔴 gare ariana                    │
│                                                     │
│ Départ: 10:37  │  Arrivée: 12:37                  │
│ Distance: 15 km │  Capacité: 30 places            │
│                                                     │
│ 🚌 bus 1                                           │
│                                                     │
│                                    [🎫 Réserver]   │
└────────────────────────────────────────────────────┘
```

### **Trajet AVEC événement (Travaux):**
```
┌────────────────────────────────────────────────────┐
│ 🟢 gare tunis → 🔴 gare ariana                    │
│                                                     │
│ Départ: 10:37  │  Arrivée: 12:37                  │
│ Distance: 15 km │  Capacité: 30 places            │
│                                                     │
│ 🚌 bus 1                                           │
│                                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ ⚠️ Attention : travaux signalés sur cette     │ │
│ │    route. Retard possible.                    │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│                                    [🎫 Réserver]   │
└────────────────────────────────────────────────────┘
```

### **Trajet AVEC événement (Accident):**
```
┌────────────────────────────────────────────────────┐
│ 🟢 gare tunis → 🔴 gare ariana                    │
│                                                     │
│ Départ: 10:37  │  Arrivée: 12:37                  │
│ Distance: 15 km │  Capacité: 30 places            │
│                                                     │
│ 🚌 bus 1                                           │
│                                                     │
│ ┌────────────────────────────────────────────────┐ │
│ │ ⚠️ Attention : accident signalé sur cette     │ │
│ │    route. Retard possible.                    │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│                                    [🎫 Réserver]   │
└────────────────────────────────────────────────────┘
```

---

## 📊 Messages d'Avertissement

| Type d'Événement | Message Affiché |
|------------------|-----------------|
| **Accident** | ⚠️ Attention : accident signalé sur cette route. Retard possible. |
| **Travaux** | ⚠️ Attention : travaux signalés sur cette route. Retard possible. |
| **Manifestation** | ⚠️ Attention : manifestation signalée sur cette route. Retard possible. |
| **Autre** | ⚠️ Attention : événement signalé sur cette route. Retard possible. |

---

## 🎯 Flux Complet

### **Étape 1: Gestionnaire crée une route**
```
Login: manager / mdp
Dashboard → Routes → Créer

Route:
├── Nom: Route A1
├── Type: Route Nationale
├── Longueur: 15 km
└── État: Bon état
→ Créer ✅
```

---

### **Étape 2: Conducteur crée un trajet sur cette route**
```
Login: driver / mdp
Dashboard → Mes Trajets → Créer

Trajet:
├── Départ: gare tunis
├── Arrivée: gare ariana
├── Type: Trajet Court
├── Route: Route A1  ← SÉLECTIONNER
├── Horaire: [Bus] 10:00 → 12:00
└── Créer ✅
```

---

### **Étape 3: Utilisateur signale un événement sur la route**
```
Login: ahmed / mdp
Dashboard → Événements → Créer

Événement:
├── Type: Travaux
├── Route: Route A1  ← MÊME ROUTE
├── Date: 2025-10-28T23:00
├── Description: Réfection de la chaussée
└── Créer ✅
```

---

### **Étape 4: Passager recherche un trajet**
```
Login: passenger / mdp
Dashboard → Rechercher un Trajet

Formulaire:
├── Ville départ: tunis
├── Ville arrivée: ariana
└── Rechercher 🔍

Résultats:
┌────────────────────────────────────────────────────┐
│ gare tunis → gare ariana                          │
│ Départ: 10:00 │ Arrivée: 12:00                   │
│ 🚌 bus 1                                          │
│                                                     │
│ ⚠️ Attention : travaux signalés sur cette route.  │
│    Retard possible.                                │
│                                                     │
│                                    [🎫 Réserver]   │
└────────────────────────────────────────────────────┘
```

**Le passager est averti avant de réserver!** ✅

---

## 🔍 Requêtes SPARQL

### **Trajet → Route → Événements:**
```sparql
# 1. Récupérer le trajet avec sa route
SELECT ?trajet ?route ?routeNom
WHERE {
    ?trajet rdf:type transport:Trajet ;
            transport:utiliseRoute ?route .
    ?route transport:nom ?routeNom .
}

# 2. Récupérer les événements sur la route
SELECT ?evenement ?typeEvenement ?type
WHERE {
    ?evenement transport:surRoute <Route_A1> ;
               rdf:type/rdfs:subClassOf* transport:ÉvénementTrafic .
    OPTIONAL { ?evenement transport:typeEvenement ?typeEvenement }
    OPTIONAL { 
        ?evenement rdf:type ?type .
        FILTER (?type != transport:ÉvénementTrafic)
    }
}
```

---

## 📈 Cas d'Usage

### **1. Sécurité Passagers**
```
Événement: Accident sur Route A1
→ Passagers avertis avant réservation
→ Peuvent choisir un autre trajet
→ Réduction des risques
```

### **2. Gestion du Trafic**
```
Événement: Travaux sur Route B2
→ Passagers informés des retards
→ Peuvent planifier en conséquence
→ Moins de frustration
```

### **3. Événements Planifiés**
```
Événement: Manifestation sur Route C3
→ Avertissement anticipé
→ Passagers peuvent éviter la route
→ Meilleure expérience utilisateur
```

---

## ✅ Avantages

### **1. Information Proactive**
- ✅ Passagers avertis AVANT de réserver
- ✅ Pas de surprise après réservation
- ✅ Meilleure expérience utilisateur

### **2. Sécurité**
- ✅ Alerte en cas d'accident
- ✅ Information sur les dangers
- ✅ Choix éclairé

### **3. Planification**
- ✅ Anticipation des retards
- ✅ Choix d'itinéraires alternatifs
- ✅ Gestion du temps

### **4. Transparence**
- ✅ Information claire et visible
- ✅ Pas de frais cachés
- ✅ Confiance accrue

---

## 🧪 Scénario de Test Complet

### **Préparation:**
```
1. Login: manager / mdp
2. Créer Route A1
3. Logout

4. Login: driver / mdp
5. Créer Trajet (tunis → ariana) sur Route A1
6. Logout

7. Login: ahmed / mdp
8. Créer Événement "Travaux" sur Route A1
9. Logout
```

---

### **Test:**
```
10. Login: passenger / mdp
11. Dashboard → Rechercher un Trajet
12. Ville départ: tunis
13. Ville arrivée: ariana
14. Rechercher 🔍

Résultat attendu:
✅ Trajet affiché
✅ Avertissement visible:
   "⚠️ Attention : travaux signalés sur cette route. Retard possible."
✅ Bandeau jaune avec bordure
✅ Bouton "Réserver" toujours disponible
```

---

### **Test avec plusieurs événements:**
```
1. Créer Événement "Accident" sur Route A1
2. Créer Événement "Manifestation" sur Route A1

Rechercher trajet:
→ Affiche l'événement le plus récent
→ Un seul avertissement par trajet
```

---

## 🎨 Personnalisation

### **Couleurs par type d'événement:**
```html
<!-- Accident: Rouge -->
{% if type_name == 'Accident' %}
<div class="border-red-300 bg-red-50 text-red-800">
    ⚠️ Attention : accident signalé...
</div>

<!-- Travaux: Jaune -->
{% elif type_name == 'Travaux' %}
<div class="border-yellow-300 bg-yellow-50 text-yellow-800">
    ⚠️ Attention : travaux signalés...
</div>

<!-- Manifestation: Orange -->
{% elif type_name == 'Manifestation' %}
<div class="border-orange-300 bg-orange-50 text-orange-800">
    ⚠️ Attention : manifestation signalée...
</div>
{% endif %}
```

---

## 🚀 Extensions Possibles

### **1. Niveau de Gravité**
```python
if type_name == 'Accident':
    trajet['warning_level'] = 'critical'
    trajet['warning'] = "🚨 URGENT : accident grave..."
elif type_name == 'Travaux':
    trajet['warning_level'] = 'warning'
    trajet['warning'] = "⚠️ Attention : travaux..."
```

### **2. Retard Estimé**
```python
if type_name == 'Travaux':
    trajet['warning'] = "⚠️ Attention : travaux signalés. Retard estimé: +30 min."
```

### **3. Routes Alternatives**
```python
if evenements:
    trajet['warning'] = "⚠️ Travaux sur cette route."
    trajet['alternative_routes'] = find_alternative_routes(trajet)
```

### **4. Historique des Événements**
```python
trajet['event_history'] = get_past_events_on_route(route_uri)
trajet['warning'] = f"⚠️ {len(evenements)} événement(s) actif(s) sur cette route."
```

---

## ✅ Résumé

### **Modifications:**
1. ✅ Nouvelle méthode `get_evenements_by_route()`
2. ✅ Logique d'avertissement dans `search_trajets_view()`
3. ✅ Affichage conditionnel dans template
4. ✅ Messages personnalisés par type d'événement

### **Résultat:**
- ✅ Passagers avertis des événements sur les routes
- ✅ Messages clairs et visibles
- ✅ Amélioration de l'expérience utilisateur
- ✅ Sécurité et transparence accrues

---

## 🎉 SYSTÈME D'AVERTISSEMENT ACTIF!

**Les passagers sont maintenant avertis des événements sur les routes avant de réserver!**

### **Test:**
```
1. Créer route + trajet + événement
2. Rechercher trajet
3. Voir l'avertissement ⚠️
4. Décider de réserver ou non
```

**Sécurité et information au service des passagers!** 🚀
