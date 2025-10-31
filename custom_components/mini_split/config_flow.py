"""Flux de configuration pour l'intégration Mini-Split"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_CONSIGNES

class MiniSplitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
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
                    vol.Required("presence_piece"): str,
                    vol.Required("presence_maison"): str,
                    vol.Optional("hysteresis", default=2): float,
                    vol.Optional("offset", default=1): float,
                })
            )

        return self.async_create_entry(
            title="Mini-Split Manager",
            data=user_input
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Renvoie le flux d'options"""
        return MiniSplitOptionsFlow(config_entry)

class MiniSplitOptionsFlow(config_entries.OptionsFlow):
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
