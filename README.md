# Mini-Split Manager pour Home Assistant

Gestion complète et intelligente de votre mini-split avec hystérésis, modes de fonctionnement avancés et détection de présence.

## ⚠️ AVERTISSEMENT IMPORTANT

**Ce projet est encore en développement et non testé en production !**
- Ne pas utiliser dans un environnement de production
- Risque d'instabilités et de comportements inattendus
- Fonctionnalités en cours de développement
- Aucune garantie d'interopérabilité

## Fonctionnalités

### Logique de contrôle avancée
- **Détection de présence intelligente** : 
  - Maison vide → Arrêt complet du mini-split
  - Pièce vide → Mode ÉCO
  - Pièce présente → Mode CONFOR

### Modes de fonctionnement saisonniers
- **Hiver** (<10°C extérieur) → Chauffage avec consignes hiver
- **Été** (≥10°C extérieur) → Climatisation avec consignes été
- **Protection** → Ne climatise pas en hiver, ne chauffe pas en été

### Logique d'hystérésis avancée
- **Chauffage** : Allume quand temp < consigne - hystérésis
- **Réduction de consigne** : Une fois atteinte, réduit de 1°C (valeur de repli)
- **Climatisation** : Inversé avec réduction de consigne

### Mode manuel
- **Détection automatique** : Détecte les modifications directes sur l'entité climate
- **Désactivation** : Seulement quand la maison est vide

## Configuration

### Entités requises
- **Mini-Split Climate** : Entité climate du mini-split à contrôler
- **Température Extérieure** : Capteur de température extérieure
- **Température Pièce** : Capteur de température de la pièce

### Entités optionnelles
- **Présence Pièce** : Capteur de détection de présence dans la pièce
- **Présence Maison** : Capteur de détection de présence dans la maison

### Paramètres configurables
- **Hystérésis** : Valeur d'hystérésis en °C (par défaut: 2)
- **Valeur de repli** : Réduction de consigne en °C (par défaut: 1)
- **Consignes de température** : Pour chaque mode (Absence, ÉCO, Confort) et saison

## Installation

1. Installez HACS
2. Ajoutez ce dépôt comme dépôt personnalisé
3. Installez "Mini-Split Manager"
4. Redémarrez Home Assistant
5. Configurez dans Configuration → Intégrations

## Limitations connues

- **Développement en cours** : Fonctionnalités incomplètes
- **Pas de tests unitaires** : Risque d'erreurs inattendues
- **Pas de support utilisateur** : À utiliser à vos risques

## Contribution

Les contributions sont les bienvenues !

## License

MIT

## Avertissement de non-responsabilité

L'utilisation de ce projet est à vos propres risques. Le développeur décline toute responsabilité pour tout dommage direct ou indirect causé par l'utilisation de ce logiciel.
