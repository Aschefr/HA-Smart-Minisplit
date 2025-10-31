"""Intégration HA Smart Minisplit pour Home Assistant"""

import asyncio
import logging
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict):
    """Configuration de base de l'intégration"""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configuration d'une entrée de configuration"""
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "coordinator": None
    }
    
    # Configurer les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Écouter les mises à jour d'options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Suppression d'une entrée de configuration"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Recharger l'entrée de configuration"""
    await hass.config_entries.async_reload(entry.entry_id)
