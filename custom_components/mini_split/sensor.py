"""Capteur pour Mini-Split"""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configuration depuis la configuration YAML"""
    async_add_entities([MiniSplitSensor(hass, config)], True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration depuis une entrée de configuration"""
    config = config_entry.data
    async_add_entities([MiniSplitSensor(hass, config)], True)

class MiniSplitSensor(SensorEntity):
    """Représentation d'un capteur Mini-Split"""

    def __init__(self, hass, config):
        self.hass = hass
        self._config = config
        self._name = "Mini-Split Status"
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Nom du capteur"""
        return self._name

    @property
    def state(self):
        """État du capteur"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Unité de mesure"""
        return TEMP_CELSIUS

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return self._attributes

    async def async_update(self):
        """Mise à jour de l'état"""
        # Récupérer les données des capteurs avec gestion d'erreur
        temp_ext = self.hass.states.get(self._config.get("temperature_exterieure"))
        temp_piece = self.hass.states.get(self._config.get("temperature_piece"))
        
        # Gestion des capteurs manquants
        if temp_ext:
            try:
                self._attributes["temperature_exterieure"] = float(temp_ext.state)
            except (ValueError, TypeError):
                self._attributes["temperature_exterieure"] = 15.0
                
        if temp_piece:
            try:
                self._attributes["temperature_piece"] = float(temp_piece.state)
            except (ValueError, TypeError):
                self._attributes["temperature_piece"] = 20.0
            
        # Déterminer l'état actuel
        presence_piece = self.hass.states.get(self._config.get("presence_piece"))
        presence_maison = self.hass.states.get(self._config.get("presence_maison"))
        
        # Gestion des capteurs manquants
        if presence_maison is None:
            presence_maison_state = "on"
        else:
            presence_maison_state = presence_maison.state if presence_maison.state else "on"
            
        if presence_piece is None:
            presence_piece_state = "on"
        else:
            presence_piece_state = presence_piece.state if presence_piece.state else "on"
        
        if presence_maison_state == "off":
            self._state = "Maison vide"
        elif presence_piece_state == "off":
            self._state = "Présence pièce : Absence"
        else:
            self._state = "Présence pièce : Présent"
            
        # Ajouter les informations de mode
        mode = self.hass.states.get("input_select.mode_climate")
        if mode:
            self._attributes["mode_climate"] = mode.state
