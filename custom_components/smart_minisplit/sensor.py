"""Capteur de statut pour HA Smart Minisplit"""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_ON, STATE_OFF

from .const import (
    DOMAIN,
    MODE_ABSENCE,
    MODE_ECO,
    MODE_CONFORT,
    SEASON_CHAUFFAGE,
    SEASON_CLIMATISATION,
    CONF_TEMP_EXT,
    CONF_TEMP_PIECE,
    CONF_PRESENCE_PIECE,
    CONF_PRESENCE_MAISON,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration du capteur de statut"""
    config = config_entry.data
    async_add_entities([SmartMinisplitStatusSensor(hass, config, config_entry.entry_id)], True)

class SmartMinisplitStatusSensor(SensorEntity):
    """Capteur de statut détaillé pour Smart Minisplit"""

    def __init__(self, hass, config, entry_id):
        self.hass = hass
        self._config = config
        self._entry_id = entry_id
        self._attr_name = "Smart Minisplit Status"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_status"
        self._state = "Initialisation"
        self._attributes = {}

    @property
    def state(self):
        """État du capteur (texte explicatif)"""
        return self._state

    @property
    def icon(self):
        """Icône du capteur"""
        return "mdi:information-outline"

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return self._attributes

    async def async_update(self):
        """Mise à jour du statut"""
        # Récupérer l'entité climate pour obtenir les informations
        climate_entity = self.hass.states.get(f"climate.{DOMAIN}_controller")
        
        if not climate_entity:
            self._state = "Contrôleur non disponible"
            return

        # Récupérer les attributs du climate
        attrs = climate_entity.attributes
        automation_enabled = attrs.get("automation_active", False)
        manual_mode = attrs.get("mode_manuel", False)
        mode_actuel = attrs.get("mode_actuel", MODE_ABSENCE)
        saison = attrs.get("saison", SEASON_CHAUFFAGE)
        target_temp = attrs.get("temperature")
        current_temp = climate_entity.state
        last_action = attrs.get("derniere_action", "Aucune action")
        
        # Récupérer les états des switches
        automation_switch = self.hass.states.get(f"switch.{DOMAIN}_automation")
        presence_piece_switch = self.hass.states.get(f"switch.{DOMAIN}_use_presence_piece")
        season_switch = self.hass.states.get(f"switch.{DOMAIN}_season")
        
        automation_active = automation_switch.state == STATE_ON if automation_switch else False
        use_presence_piece = presence_piece_switch.state == STATE_ON if presence_piece_switch else False
        season_mode = "Chauffage" if (season_switch and season_switch.state == STATE_ON) else "Climatisation"
        
        # Récupérer les températures
        temp_ext_entity = self.hass.states.get(self._config.get(CONF_TEMP_EXT))
        temp_piece_entity = self.hass.states.get(self._config.get(CONF_TEMP_PIECE))
        
        temp_ext = "N/A"
        temp_piece = "N/A"
        
        if temp_ext_entity:
            try:
                temp_ext = f"{float(temp_ext_entity.state):.1f}°C"
            except (ValueError, TypeError):
                pass
                
        if temp_piece_entity:
            try:
                temp_piece = f"{float(temp_piece_entity.state):.1f}°C"
            except (ValueError, TypeError):
                pass
        
        # Récupérer les états de présence
        presence_maison_entity = self.hass.states.get(self._config.get(CONF_PRESENCE_MAISON))
        presence_piece_entity = self.hass.states.get(self._config.get(CONF_PRESENCE_PIECE))
        
        presence_maison = "Présente" if (presence_maison_entity is None or presence_maison_entity.state == STATE_ON) else "Vide"
        presence_piece = "Présente" if (presence_piece_entity is None or presence_piece_entity.state == STATE_ON) else "Vide"
        
        # Construire le message de statut détaillé
        if not automation_active:
            self._state = "⏸️ GESTION AUTOMATIQUE DÉSACTIVÉE - Le mini-split n'est pas contrôlé automatiquement"
            self._attributes = {
                "automation": "Désactivée",
                "action": "Aucune - Contrôle manuel uniquement",
            }
        elif manual_mode:
            self._state = f"🖐️ MODE MANUEL ACTIF - Dernière action: {last_action}"
            self._attributes = {
                "automation": "Active (en pause)",
                "mode_manuel": "Actif",
                "raison": "L'utilisateur a modifié manuellement le mini-split",
                "note": "Le mode manuel se désactivera automatiquement quand la maison sera vide",
            }
        else:
            # Construire le message selon le contexte
            if presence_maison == "Vide":
                self._state = f"🏠 MAISON VIDE - Mini-split arrêté pour économie d'énergie"
                raison = "Personne n'est à la maison"
            elif mode_actuel == MODE_ABSENCE:
                self._state = f"💤 MODE ABSENCE - Mini-split arrêté"
                raison = "Mode absence activé"
            elif mode_actuel == MODE_ECO:
                consigne = f"{target_temp}°C" if target_temp else "N/A"
                self._state = f"🌱 MODE ECO - {season_mode} à {consigne} (pièce vide)"
                raison = f"Pièce vide détectée, passage en mode économique"
            else:  # MODE_CONFORT
                consigne = f"{target_temp}°C" if target_temp else "N/A"
                self._state = f"🏡 MODE CONFORT - {season_mode} à {consigne} (pièce occupée)"
                raison = f"Présence détectée dans la pièce, confort maximal"
            
            self._attributes = {
                "automation": "Active",
                "mode_actuel": mode_actuel.upper(),
                "saison": season_mode,
                "temperature_exterieure": temp_ext,
                "temperature_piece": temp_piece,
                "consigne_actuelle": f"{target_temp}°C" if target_temp else "N/A",
                "presence_maison": presence_maison,
                "presence_piece": presence_piece,
                "utilise_presence_piece": "Oui" if use_presence_piece else "Non",
                "derniere_action": last_action,
                "raison": raison,
            }
        
        # Ajouter des informations générales
        self._attributes["mode_manuel"] = "Actif" if manual_mode else "Inactif"
