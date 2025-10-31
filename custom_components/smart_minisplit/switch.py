"""Switches pour HA Smart Minisplit"""

import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON

from .const import DOMAIN, SEASON_CHAUFFAGE, SEASON_CLIMATISATION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration des switches"""
    switches = [
        SmartMinisplitAutomationSwitch(hass, config_entry.entry_id),
        SmartMinisplitPresencePieceSwitch(hass, config_entry.entry_id),
        SmartMinisplitSeasonSwitch(hass, config_entry.entry_id),
    ]
    async_add_entities(switches, True)

class SmartMinisplitAutomationSwitch(SwitchEntity):
    """Switch pour activer/désactiver la gestion automatique"""

    def __init__(self, hass, entry_id):
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = "Smart Minisplit Automation"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_automation"
        self._is_on = True

    @property
    def is_on(self):
        """Retourne True si le switch est ON"""
        return self._is_on

    @property
    def icon(self):
        """Icône du switch"""
        return "mdi:auto-fix" if self._is_on else "mdi:cancel"

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return {
            "description": "Active ou désactive la gestion automatique du mini-split",
            "status": "Actif" if self._is_on else "Inactif"
        }

    async def async_turn_on(self, **kwargs):
        """Activer la gestion automatique"""
        self._is_on = True
        self.async_write_ha_state()
        _LOGGER.info("Gestion automatique activée")

    async def async_turn_off(self, **kwargs):
        """Désactiver la gestion automatique"""
        self._is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Gestion automatique désactivée - Le mini-split ne sera pas modifié")

class SmartMinisplitPresencePieceSwitch(SwitchEntity):
    """Switch pour activer/désactiver l'utilisation de la présence pièce"""

    def __init__(self, hass, entry_id):
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = "Smart Minisplit Use Presence Piece"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_use_presence_piece"
        self._is_on = True

    @property
    def is_on(self):
        """Retourne True si le switch est ON"""
        return self._is_on

    @property
    def icon(self):
        """Icône du switch"""
        return "mdi:motion-sensor" if self._is_on else "mdi:motion-sensor-off"

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return {
            "description": "Active ou désactive le passage ECO/CONFORT selon la présence dans la pièce",
            "status": "Utilise présence pièce" if self._is_on else "Ignore présence pièce"
        }

    async def async_turn_on(self, **kwargs):
        """Activer l'utilisation de la présence pièce"""
        self._is_on = True
        self.async_write_ha_state()
        _LOGGER.info("Utilisation de la présence pièce activée")

    async def async_turn_off(self, **kwargs):
        """Désactiver l'utilisation de la présence pièce"""
        self._is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Utilisation de la présence pièce désactivée - Mode CONFORT permanent")

class SmartMinisplitSeasonSwitch(SwitchEntity):
    """Switch pour sélectionner la saison (Chauffage/Climatisation)"""

    def __init__(self, hass, entry_id):
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = "Smart Minisplit Season"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_season"
        self._is_on = True  # ON = Chauffage, OFF = Climatisation

    @property
    def is_on(self):
        """Retourne True si le switch est ON (Chauffage)"""
        return self._is_on

    @property
    def icon(self):
        """Icône du switch"""
        return "mdi:fire" if self._is_on else "mdi:snowflake"

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return {
            "description": "Sélectionne le mode Chauffage ou Climatisation",
            "saison_actuelle": SEASON_CHAUFFAGE if self._is_on else SEASON_CLIMATISATION,
            "mode": "Chauffage" if self._is_on else "Climatisation"
        }

    async def async_turn_on(self, **kwargs):
        """Passer en mode Chauffage"""
        self._is_on = True
        self.async_write_ha_state()
        _LOGGER.info("Mode Chauffage sélectionné")

    async def async_turn_off(self, **kwargs):
        """Passer en mode Climatisation"""
        self._is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Mode Climatisation sélectionné")
