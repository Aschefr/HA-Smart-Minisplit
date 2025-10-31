# HA Smart Minisplit pour Home Assistant

Gestion complète et intelligente de votre mini-split avec contrôle automatique avancé, détection de présence et optimisation énergétique.

## ✨ Fonctionnalités

### 🎛️ Contrôle Automatique Complet

- **Switch d'activation/désactivation globale** : Activez ou désactivez la gestion automatique à tout moment
- **3 Modes de fonctionnement** : Absence, Eco, Confort
- **2 Saisons** : Chauffage et Climatisation (sélection manuelle via switch)
- **Consignes configurables** : Pour chaque mode et chaque saison (6 consignes au total)

### 🧠 Logique Intelligente

#### Détection de Présence
- **Présence Maison** : Si vide → Arrêt complet du mini-split
- **Présence Pièce** : Si vide → Mode ECO / Si occupée → Mode CONFORT
- **Switch d'activation** : Possibilité de désactiver la détection de présence pièce

#### Hystérésis et Repli Économique
- **Hystérésis** : Évite les cycles courts marche/arrêt
- **Offset de repli** : Une fois la consigne atteinte, réduit la consigne de X°C pour économiser l'énergie
  - **Chauffage** : Réduit de X°C quand temp ≥ consigne + offset
  - **Climatisation** : Augmente de X°C quand temp ≤ consigne - offset

#### Mode Manuel Intelligent
- **Détection automatique** : Détecte quand l'utilisateur modifie directement le mini-split
- **Pause automatique** : Met en pause le pilotage automatique
- **Réactivation automatique** : Se désactive automatiquement quand la maison est vide

### 📊 Monitoring Détaillé

#### Entité Sensor de Statut
Affiche en texte clair :
- L'état actuel de l'automatisation
- Le mode en cours (Absence/Eco/Confort)
- Les températures (extérieure, pièce, consigne)
- Les présences détectées
- La dernière action effectuée et sa raison

Exemples de messages :
- `🏠 MAISON VIDE - Mini-split arrêté pour économie d'énergie`
- `🏡 MODE CONFORT - Chauffage à 22°C (pièce occupée)`
- `🌱 MODE ECO - Climatisation à 25°C (pièce vide)`
- `🖐️ MODE MANUEL ACTIF - Dernière action: Mode manuel détecté - Consigne modifiée de 22°C à 24°C`

## 🔧 Configuration

### Prérequis

Vous devez avoir dans Home Assistant :
- Une entité `climate` pour votre mini-split
- Un capteur de température extérieure
- Un capteur de température de la pièce
- (Optionnel) Un capteur de présence dans la pièce
- (Optionnel) Un capteur de présence dans la maison

### Installation via HACS

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Intégrations"
3. Cliquez sur le menu (⋮) en haut à droite
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez l'URL : `https://github.com/Aschefr/HA-Smart-Minisplit`
6. Catégorie : "Intégration"
7. Recherchez "HA Smart Minisplit" et installez
8. Redémarrez Home Assistant

### Configuration Initiale

1. Allez dans **Configuration** → **Appareils et services**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **Smart Minisplit**
4. Remplissez le formulaire :

#### Étape 1 - Entités
- **Mini-Split Climate** : Sélectionnez votre entité climate existante
- **Température Extérieure** : Capteur de température extérieure
- **Température Pièce** : Capteur de température de la pièce
- **Présence Pièce** (optionnel) : Capteur de présence dans la pièce
- **Présence Maison** (optionnel) : Capteur de présence globale
- **Hystérésis** : Valeur en °C (défaut: 2.0)
- **Offset** : Valeur de repli en °C (défaut: 1.0)

#### Étape 2 - Consignes
- **Consignes Chauffage** : Absence (18°C), Eco (20°C), Confort (22°C)
- **Consignes Climatisation** : Absence (26°C), Eco (25°C), Confort (24°C)

## 🎮 Utilisation

### Entités Créées

Après configuration, vous aurez accès à :

#### Switches
- `switch.smart_minisplit_automation` : Active/désactive la gestion automatique
- `switch.smart_minisplit_use_presence_piece` : Active/désactive l'utilisation de la présence pièce
- `switch.smart_minisplit_season` : Sélectionne Chauffage (ON) ou Climatisation (OFF)

#### Climate
- `climate.smart_minisplit_controller` : Contrôleur principal avec tous les attributs

#### Sensor
- `sensor.smart_minisplit_status` : Statut détaillé en texte clair

### Exemples d'Automatisations

#### Activation automatique selon la saison
```yaml
automation:
  - alias: "Mini-split - Passage automatique Hiver/Été"
    trigger:
      - platform: numeric_state
        entity_id: sensor.temperature_exterieure
        below: 10
        for: "02:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.smart_minisplit_season
```

#### Notification en mode manuel
```yaml
automation:
  - alias: "Mini-split - Notification mode manuel"
    trigger:
      - platform: state
        entity_id: climate.smart_minisplit_controller
        attribute: mode_manuel
        to: true
    action:
      - service: notify.mobile_app
        data:
          message: "Mode manuel détecté sur le mini-split"
```

## 📖 Fonctionnement Détaillé

### Logique de Décision

```
┌─────────────────────────────────────┐
│  Automation désactivée ?            │
│  → Aucune action                    │
└─────────────────────────────────────┘
            ↓ Non
┌─────────────────────────────────────┐
│  Mode manuel actif ?                │
│  → Pause du pilotage automatique   │
└─────────────────────────────────────┘
            ↓ Non
┌─────────────────────────────────────┐
│  Maison vide ?                      │
│  → Arrêt complet                    │
│  → Désactive le mode manuel         │
└─────────────────────────────────────┘
            ↓ Non
┌─────────────────────────────────────┐
│  Pièce vide ET switch présence ON ? │
│  → Mode ECO                         │
└─────────────────────────────────────┘
            ↓ Non
┌─────────────────────────────────────┐
│  → Mode CONFORT                     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  Appliquer hystérésis + repli       │
└─────────────────────────────────────┘
```

### Logique d'Hystérésis avec Repli

#### Mode Chauffage
1. Si `temp < consigne - hystérésis` → Active chauffage à consigne normale
2. Si `temp ≥ consigne + offset` → Réduit consigne de `offset` (repli économique)

#### Mode Climatisation
1. Si `temp > consigne + hystérésis` → Active climatisation à consigne normale
2. Si `temp ≤ consigne - offset` → Augmente consigne de `offset` (repli économique)

## 🔍 Dépannage

### Le mini-split ne s'allume pas
- Vérifiez que `switch.smart_minisplit_automation` est sur ON
- Vérifiez que le mode manuel n'est pas actif
- Consultez `sensor.smart_minisplit_status` pour voir la raison

### Le mode manuel ne se désactive pas
- Le mode manuel se désactive uniquement quand la maison est détectée vide
- Vérifiez votre capteur de présence maison

### Les consignes ne correspondent pas
- Consultez les attributs de `climate.smart_minisplit_controller`
- Vérifiez la logique de repli (offset appliqué)

## 📝 Logs

Pour activer les logs détaillés, ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.smart_minisplit: debug
```

## 🤝 Contribution

Les contributions sont les bienvenues !

## 📄 Licence

MIT

## ⚠️ Avertissement

Cette intégration contrôle directement votre équipement de chauffage/climatisation. Utilisez-la à vos propres risques. L'auteur décline toute responsabilité pour les dommages matériels ou la surconsommation énergétique.

## 🆘 Support

Pour toute question ou problème :
- [Issues GitHub](https://github.com/Aschefr/HA-Smart-Minisplit/issues)
- [Discussions GitHub](https://github.com/Aschefr/HA-Smart-Minisplit/discussions)
