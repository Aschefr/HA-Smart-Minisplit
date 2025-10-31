"""Flux de configuration pour l'intégration HA Smart Minisplit"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_CONSIGNES

class SmartMinisplitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestion du flux de configuration"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLLING

    async def async_step_user(self, user_input=None):
        """Étape de configuration initiale"""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("mini_split_climate"): str,
                    vol.Required("temperature_exterieure"): str,
                    vol.Required("temperature_piece"): str,
                    vol.Optional("presence_piece"): str,
                    vol.Optional("presence_maison"): str,
                    vol.Optional("hysteresis", default=2): float,
                    vol.Optional("repli", default=1): float,
                    vol.Optional("consigne_absence_chauffage", default=18): float,
                    vol.Optional("consigne_eco_chauffage", default=20): float,
                    vol.Optional("consigne_confort_chauffage", default=22): float,
                    vol.Optional("consigne_absence_climatisation", default=26): float,
                    vol.Optional("consigne_eco_climatisation", default=25): float,
                    vol.Optional("consigne_confort_climatisation", default=24): float,
                })
            )

        return self.async_create_entry(
            title="HA Smart Minisplit",
            data=user_input
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Renvoie le flux d'options"""
        return SmartMinisplitOptionsFlow(config_entry)

class SmartMinisplitOptionsFlow(config_entries.OptionsFlow):
    """Gestion des options"""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Étape d'initialisation des options"""
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Optional(
                        "consigne_absence_chauffage",
                        default=self.config_entry.data.get(
                            "consigne_absence_chauffage", 
                            DEFAULT_CONSIGNES["absence"]["chauffage"]
                        )
                    ): float,
                    vol.Optional(
                        "consigne_eco_chauffage",
                        default=self.config_entry.data.get(
                            "consigne_eco_chauffage", 
                            DEFAULT_CONSIGNES["eco"]["chauffage"]
                        )
                    ): float,
                    vol.Optional(
                        "consigne_confort_chauffage",
                        default=self.config_entry.data.get(
                            "consigne_confort_chauffage", 
                            DEFAULT_CONSIGNES["confort"]["chauffage"]
                        )
                    ): float,
                    vol.Optional(
                        "consigne_absence_climatisation",
                        default=self.config_entry.data.get(
                            "consigne_absence_climatisation", 
                            DEFAULT_CONSIGNES["absence"]["climatisation"]
                        )
                    ): float,
                    vol.Optional(
                        "consigne_eco_climatisation",
                        default=self.config_entry.data.get(
                            "consigne_eco_climatisation", 
                            DEFAULT_CONSIGNES["eco"]["climatisation"]
                        )
                    ): float,
                    vol.Optional(
                        "consigne_confort_climatisation",
                        default=self.config_entry.data.get(
                            "consigne_confort_climatisation", 
                            DEFAULT_CONSIGNES["confort"]["climatisation"]
                        )
                    ): float,
                })
            )

        return self.async_create_entry(title="", data=user_input)
