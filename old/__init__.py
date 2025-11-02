"""HA Smart Minisplit Integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "smart_minisplit"

async def async_setup(hass: HomeAssistant, config: dict):
    """Configuration de base de l'intégration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configuration d'une entrée de configuration."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await hass.config_entries.async_forward_entry_setups(entry, ["climate", "sensor", "switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Suppression d'une entrée de configuration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["climate", "sensor", "switch"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
