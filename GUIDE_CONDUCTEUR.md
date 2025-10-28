# 🚗 GUIDE CONDUCTEUR - Gérer les Réservations

## ⚠️ IMPORTANT: Vous êtes sur la mauvaise page!

### ❌ Page Actuelle: "Gestion des Trajets"
Cette page sert uniquement à **créer/modifier/supprimer vos trajets**.  
Elle n'affiche PAS les réservations!

---

## ✅ Page Correcte: "Réservations"

### 📍 Comment y accéder:

#### **Option 1: Depuis le Dashboard**
```
1. Cliquer sur "Dashboard" (en haut à droite)
2. Scroller vers le bas
3. Section "Informations Utiles"
4. Cliquer sur la carte "Réservations" 🎫
   (Icône ticket jaune/bleu)
```

#### **Option 2: URL Directe**
```
http://localhost:8000/accounts/mes-reservations-conducteur/
```

---

## 🎯 Ce que vous verrez sur la page "Réservations"

### Si vous avez des réservations:

```
┌─────────────────────────────────────────────────────┐
│ 📋 Gérer les Réservations                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 🗺️ gare tunis → gare ariana                        │
│                                                     │
│ Passager: User_ahmed                                │
│ Date: 2025-10-28                                    │
│ Places: 2                                           │
│ Statut: 🟡 En attente                              │
│                                                     │
│ [✅ Confirmer]  [❌ Refuser]                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Actions disponibles:

1. **Bouton vert "Confirmer"** ✅
   - Change le statut à "Confirmée"
   - Le passager voit sa réservation confirmée

2. **Bouton rouge "Refuser"** ❌
   - Change le statut à "Annulée"
   - Le passager voit sa réservation refusée

---

## 🔍 Différence entre les 2 pages

| Page | URL | Fonction |
|------|-----|----------|
| **Gestion des Trajets** | `/trajets/` | Créer/Modifier/Supprimer VOS trajets |
| **Réservations** | `/mes-reservations-conducteur/` | Confirmer/Refuser les réservations des passagers |

---

## 📸 Où trouver le lien "Réservations" dans le Dashboard

Votre dashboard conducteur a **2 sections**:

### **Section 1: Actions Principales** (3 grandes cartes)
- Mes Trajets 🛣️
- Mon Véhicule 🚗
- Mes Statistiques 📊

### **Section 2: Informations Utiles** (5 petites cartes)
- **Réservations 🎫** ← C'EST ICI!
- Horaires ⏰
- Stations 📍
- Alertes Trafic ⚠️
- Mes Avis ⭐

---

## 🧪 Test Rapide

1. **Retourner au Dashboard**
   ```
   Cliquer sur "Dashboard" en haut
   ```

2. **Scroller vers le bas**
   ```
   Passer les 3 grandes cartes
   Voir la section "Informations Utiles"
   ```

3. **Cliquer sur "Réservations"**
   ```
   Carte avec icône ticket 🎫
   Texte: "Gérer réservations"
   ```

4. **Vous devriez voir:**
   ```
   - Titre: "Gérer les Réservations"
   - Liste des réservations pour VOS trajets
   - Boutons Confirmer/Refuser
   ```

---

## ❓ Si vous ne voyez toujours pas le lien

### Vérification 1: Êtes-vous connecté en tant que CONDUCTEUR?
```
En haut à droite → Voir votre nom d'utilisateur
Si c'est "driver" → OK ✅
Si c'est "ahmed" → C'est un PASSAGER ❌
Si c'est "manager" → C'est un GESTIONNAIRE ❌
```

### Vérification 2: Rechargez la page
```
Appuyez sur F5 ou Ctrl+R
```

### Vérification 3: URL directe
```
Tapez directement dans le navigateur:
http://localhost:8000/accounts/mes-reservations-conducteur/
```

---

## 🎯 Résumé

**Pour gérer les réservations en tant que conducteur:**

1. ❌ NE PAS aller dans "Gestion des Trajets"
2. ✅ Aller dans "Réservations" (section Informations Utiles du Dashboard)
3. ✅ Ou utiliser l'URL: `/mes-reservations-conducteur/`

**C'est tout!** 🚀
