"""Flux de configuration pour l'intégration HA Smart Minisplit"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import (
    DOMAIN, 
    DEFAULT_CONSIGNES,
    DEFAULT_HYSTERESIS,
    DEFAULT_OFFSET,
    CONF_MINI_SPLIT,
    CONF_TEMP_EXT,
    CONF_TEMP_PIECE,
    CONF_PRESENCE_PIECE,
    CONF_PRESENCE_MAISON,
    CONF_HYSTERESIS,
    CONF_OFFSET,
    CONF_CONSIGNE_ABSENCE_CHAUFFAGE,
    CONF_CONSIGNE_ECO_CHAUFFAGE,
    CONF_CONSIGNE_CONFORT_CHAUFFAGE,
    CONF_CONSIGNE_ABSENCE_CLIMATISATION,
    CONF_CONSIGNE_ECO_CLIMATISATION,
    CONF_CONSIGNE_CONFORT_CLIMATISATION,
)

# Correction : Retrait de ", domain=DOMAIN" et de la faute de frappe
class SmartMinisplitConfigFlow(config_entries.ConfigFlow):
    """Gestion du flux de configuration"""

    VERSION = 2
    # CORRECTION : Remplacer CONN_CLASS_LOCAL_POLLING par CONN_CLASS_LOCAL_POLL
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Étape de configuration initiale"""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_MINI_SPLIT): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate")
                    ),
                    vol.Required(CONF_TEMP_EXT): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Required(CONF_TEMP_PIECE): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Optional(CONF_PRESENCE_PIECE): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["binary_sensor", "input_boolean"])
                    ),
                    vol.Optional(CONF_PRESENCE_MAISON): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["binary_sensor", "input_boolean"])
                    ),
                    vol.Optional(CONF_HYSTERESIS, default=DEFAULT_HYSTERESIS): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=5.0)
                    ),
                    vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=3.0)
                    ),
                })
            )

        return await self.async_step_consignes(user_input)

    async def async_step_consignes(self, user_input):
        """Étape de configuration des consignes"""
        if "step_data" not in self.context:
            self.context["step_data"] = user_input
            
            return self.async_show_form(
                step_id="consignes",
                data_schema=vol.Schema({
                    vol.Optional(CONF_CONSIGNE_ABSENCE_CHAUFFAGE, 
                                 default=DEFAULT_CONSIGNES["absence"]["chauffage"]): vol.All(
                        vol.Coerce(float), vol.Range(min=15.0, max=25.0)
                    ),
                    vol.Optional(CONF_CONSIGNE_ECO_CHAUFFAGE,
                                 default=DEFAULT_CONSIGNES["eco"]["chauffage"]): vol.All(
                        vol.Coerce(float), vol.Range(min=15.0, max=25.0)
                    ),
                    vol.Optional(CONF_CONSIGNE_CONFORT_CHAUFFAGE,
                                 default=DEFAULT_CONSIGNES["confort"]["chauffage"]): vol.All(
                        vol.Coerce(float), vol.Range(min=15.0, max=25.0)
                    ),
                    vol.Optional(CONF_CONSIGNE_ABSENCE_CLIMATISATION,
                                 default=DEFAULT_CONSIGNES["absence"]["climatisation"]): vol.All(
                        vol.Coerce(float), vol.Range(min=20.0, max=30.0)
                    ),
                    vol.Optional(CONF_CONSIGNE_ECO_CLIMATISATION,
                                 default=DEFAULT_CONSIGNES["eco"]["climatisation"]): vol.All(
                        vol.Coerce(float), vol.Range(min=20.0, max=30.0)
                    ),
                    vol.Optional(CONF_CONSIGNE_CONFORT_CLIMATISATION,
                                 default=DEFAULT_CONSIGNES["confort"]["climatisation"]): vol.All(
                        vol.Coerce(float), vol.Range(min=20.0, max=30.0)
                    ),
                })
            )
        
        # Fusionner les données des deux étapes
        final_data = {**self.context["step_data"], **user_input}
        
        return self.async_create_entry(
            title="Smart Minisplit",
            data=final_data
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
        """Étape d'initialisation des options (Consignes et Réglages)"""
        
        # Utiliser les données actuelles de l'entrée de configuration
        data = self.config_entry.data
        
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    # Réglages généraux
                    vol.Optional(
                        CONF_HYSTERESIS,
                        default=data.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS)
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=5.0)),
                    vol.Optional(
                        CONF_OFFSET,
                        default=data.get(CONF_OFFSET, DEFAULT_OFFSET)
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=3.0)),

                    # Consignes CHAUFFAGE
                    vol.Optional(
                        CONF_CONSIGNE_ABSENCE_CHAUFFAGE,
                        default=data.get(CONF_CONSIGNE_ABSENCE_CHAUFFAGE, DEFAULT_CONSIGNES["absence"]["chauffage"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=15.0, max=25.0)),
                    vol.Optional(
                        CONF_CONSIGNE_ECO_CHAUFFAGE,
                        default=data.get(CONF_CONSIGNE_ECO_CHAUFFAGE, DEFAULT_CONSIGNES["eco"]["chauffage"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=15.0, max=25.0)),
                    vol.Optional(
                        CONF_CONSIGNE_CONFORT_CHAUFFAGE,
                        default=data.get(CONF_CONSIGNE_CONFORT_CHAUFFAGE, DEFAULT_CONSIGNES["confort"]["chauffage"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=15.0, max=25.0)),

                    # Consignes CLIMATISATION
                    vol.Optional(
                        CONF_CONSIGNE_ABSENCE_CLIMATISATION,
                        default=data.get(CONF_CONSIGNE_ABSENCE_CLIMATISATION, DEFAULT_CONSIGNES["absence"]["climatisation"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=20.0, max=30.0)),
                    vol.Optional(
                        CONF_CONSIGNE_ECO_CLIMATISATION,
                        default=data.get(CONF_CONSIGNE_ECO_CLIMATISATION, DEFAULT_CONSIGNES["eco"]["climatisation"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=20.0, max=30.0)),
                    vol.Optional(
                        CONF_CONSIGNE_CONFORT_CLIMATISATION,
                        default=data.get(CONF_CONSIGNE_CONFORT_CLIMATISATION, DEFAULT_CONSIGNES["confort"]["climatisation"])
                    ): vol.All(vol.Coerce(float), vol.Range(min=20.0, max=30.0)),
                })
            )
        
        # Enregistrer les options
        return self.async_create_entry(title="", data=user_input)
