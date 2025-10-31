"""Entité Climate pour HA Smart Minisplit"""

import logging
from datetime import timedelta
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    MODE_ABSENCE,
    MODE_ECO,
    MODE_CONFORT,
    SEASON_CHAUFFAGE,
    SEASON_CLIMATISATION,
    STATE_MANUAL,
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

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration depuis une entrée de configuration"""
    config = config_entry.data
    async_add_entities([SmartMinisplitClimate(hass, config, config_entry.entry_id)], True)

class SmartMinisplitClimate(ClimateEntity):
    """Représentation du contrôleur Smart Minisplit"""

    def __init__(self, hass, config, entry_id):
        self.hass = hass
        self._config = config
        self._entry_id = entry_id
        self._attr_name = "Smart Minisplit Controller"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_climate"
        
        # État interne
        self._current_temperature = None
        self._target_temperature = None
        self._hvac_mode = HVACMode.OFF
        self._season = SEASON_CHAUFFAGE
        self._mode_actuel = MODE_ABSENCE
        self._automation_enabled = True
        self._manual_mode = False
        self._use_presence_piece = True
        self._last_action = "Initialisation"
        
        # Température réelle du mini-split
        self._minisplit_target = None
        self._minisplit_mode = None
        
        # Paramètres
        self._hysteresis = config.get(CONF_HYSTERESIS, 2.0)
        self._offset = config.get(CONF_OFFSET, 1.0)
        
        # Écoute des changements sur le mini-split réel
        self._unsub_mini_split = None

    @property
    def temperature_unit(self):
        """Unité de température"""
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Température actuelle de la pièce"""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Température cible calculée"""
        return self._target_temperature

    @property
    def hvac_mode(self):
        """Mode HVAC actuel"""
        return self._hvac_mode

    @property
    def hvac_modes(self):
        """Modes HVAC disponibles"""
        return [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]

    @property
    def supported_features(self):
        """Fonctionnalités supportées"""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires"""
        return {
            "saison": self._season,
            "mode_actuel": self._mode_actuel,
            "automation_active": self._automation_enabled,
            "mode_manuel": self._manual_mode,
            "utiliser_presence_piece": self._use_presence_piece,
            "hysteresis": self._hysteresis,
            "offset": self._offset,
            "derniere_action": self._last_action,
            "minisplit_target": self._minisplit_target,
            "minisplit_mode": self._minisplit_mode,
        }

    async def async_added_to_hass(self):
        """Appelé quand l'entité est ajoutée à Home Assistant"""
        # Écouter les changements sur le mini-split réel
        mini_split_entity = self._config.get(CONF_MINI_SPLIT)
        if mini_split_entity:
            self._unsub_mini_split = async_track_state_change_event(
                self.hass, [mini_split_entity], self._async_mini_split_changed
            )

    async def async_will_remove_from_hass(self):
        """Appelé quand l'entité est supprimée"""
        if self._unsub_mini_split:
            self._unsub_mini_split()

    @callback
    async def _async_mini_split_changed(self, event):
        """Appelé quand le mini-split réel change"""
        if not self._automation_enabled:
            return
            
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Récupérer l'état actuel du mini-split
        minisplit_temp = new_state.attributes.get("temperature")
        minisplit_mode = new_state.state

        # Détecter si l'utilisateur a modifié manuellement
        if self._target_temperature and minisplit_temp:
            if abs(float(minisplit_temp) - self._target_temperature) > 0.5:
                self._manual_mode = True
                self._last_action = f"Mode manuel détecté - Consigne modifiée de {self._target_temperature}°C à {minisplit_temp}°C"
                _LOGGER.info(self._last_action)
                self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Définir le mode HVAC (non utilisé directement)"""
        pass

    async def async_set_temperature(self, **kwargs):
        """Définir la température (non utilisé directement)"""
        pass

    async def async_update(self):
        """Mise à jour de l'état avec logique complète"""
        # Récupérer l'état des switches de contrôle
        automation_switch = self.hass.states.get(f"switch.{DOMAIN}_automation")
        if automation_switch:
            self._automation_enabled = automation_switch.state == STATE_ON
        
        presence_piece_switch = self.hass.states.get(f"switch.{DOMAIN}_use_presence_piece")
        if presence_piece_switch:
            self._use_presence_piece = presence_piece_switch.state == STATE_ON
        
        # Si automation désactivée, ne rien faire
        if not self._automation_enabled:
            self._last_action = "Gestion automatique désactivée"
            return

        # Récupérer les températures
        temp_ext_entity = self.hass.states.get(self._config.get(CONF_TEMP_EXT))
        temp_piece_entity = self.hass.states.get(self._config.get(CONF_TEMP_PIECE))
        
        temp_ext = 15.0
        temp_piece = 20.0
        
        if temp_ext_entity:
            try:
                temp_ext = float(temp_ext_entity.state)
            except (ValueError, TypeError):
                pass
                
        if temp_piece_entity:
            try:
                temp_piece = float(temp_piece_entity.state)
                self._current_temperature = temp_piece
            except (ValueError, TypeError):
                pass

        # Déterminer la saison depuis le switch
        season_switch = self.hass.states.get(f"switch.{DOMAIN}_season")
        if season_switch:
            self._season = SEASON_CHAUFFAGE if season_switch.state == STATE_ON else SEASON_CLIMATISATION

        # Récupérer les états de présence
        presence_maison_entity = self.hass.states.get(self._config.get(CONF_PRESENCE_MAISON))
        presence_piece_entity = self.hass.states.get(self._config.get(CONF_PRESENCE_PIECE))
        
        presence_maison = STATE_ON if presence_maison_entity is None else presence_maison_entity.state
        presence_piece = STATE_ON if presence_piece_entity is None else presence_piece_entity.state

        # Désactiver le mode manuel si la maison est vide
        if presence_maison == STATE_OFF and self._manual_mode:
            self._manual_mode = False
            self._last_action = "Mode manuel désactivé - Maison vide détectée"
            _LOGGER.info(self._last_action)

        # Si mode manuel, ne pas modifier la consigne
        if self._manual_mode:
            return

        # Déterminer le mode en fonction de la présence
        old_mode = self._mode_actuel
        
        if presence_maison == STATE_OFF:
            self._mode_actuel = MODE_ABSENCE
            self._hvac_mode = HVACMode.OFF
            self._target_temperature = None
            self._last_action = "Maison vide - Arrêt du mini-split"
            await self._control_minisplit()
            return
        elif self._use_presence_piece and presence_piece == STATE_OFF:
            self._mode_actuel = MODE_ECO
        else:
            self._mode_actuel = MODE_CONFORT

        # Récupérer la consigne selon le mode et la saison
        consigne = self._get_consigne()
        self._target_temperature = consigne

        # Déterminer le mode HVAC
        if self._season == SEASON_CHAUFFAGE:
            self._hvac_mode = HVACMode.HEAT
        else:
            self._hvac_mode = HVACMode.COOL

        # Appliquer la logique d'hystérésis avec repli
        await self._apply_hysteresis_with_repli(temp_piece)

        # Logger l'action
        if old_mode != self._mode_actuel:
            self._last_action = f"Passage en mode {self._mode_actuel.upper()} - Consigne: {self._target_temperature}°C"
            _LOGGER.info(self._last_action)

    def _get_consigne(self):
        """Récupérer la consigne selon le mode et la saison"""
        if self._season == SEASON_CHAUFFAGE:
            if self._mode_actuel == MODE_ABSENCE:
                return self._config.get(CONF_CONSIGNE_ABSENCE_CHAUFFAGE, 18.0)
            elif self._mode_actuel == MODE_ECO:
                return self._config.get(CONF_CONSIGNE_ECO_CHAUFFAGE, 20.0)
            else:
                return self._config.get(CONF_CONSIGNE_CONFORT_CHAUFFAGE, 22.0)
        else:
            if self._mode_actuel == MODE_ABSENCE:
                return self._config.get(CONF_CONSIGNE_ABSENCE_CLIMATISATION, 26.0)
            elif self._mode_actuel == MODE_ECO:
                return self._config.get(CONF_CONSIGNE_ECO_CLIMATISATION, 25.0)
            else:
                return self._config.get(CONF_CONSIGNE_CONFORT_CLIMATISATION, 24.0)

    async def _apply_hysteresis_with_repli(self, temp_piece):
        """Appliquer l'hystérésis avec logique de repli"""
        if self._target_temperature is None:
            return

        consigne_base = self._get_consigne()
        
        if self._season == SEASON_CHAUFFAGE:
            # Mode chauffage
            if temp_piece < self._target_temperature - self._hysteresis:
                # Trop froid - activer le chauffage à consigne normale
                self._target_temperature = consigne_base
                self._last_action = f"Température {temp_piece}°C < consigne-hystérésis ({self._target_temperature-self._hysteresis}°C) - Chauffage activé à {self._target_temperature}°C"
                await self._control_minisplit()
            elif temp_piece >= self._target_temperature + self._offset:
                # Consigne atteinte + offset - passer en repli
                self._target_temperature = consigne_base - self._offset
                self._last_action = f"Consigne atteinte+offset ({temp_piece}°C) - Repli à {self._target_temperature}°C pour économie d'énergie"
                await self._control_minisplit()
        else:
            # Mode climatisation
            if temp_piece > self._target_temperature + self._hysteresis:
                # Trop chaud - activer la climatisation à consigne normale
                self._target_temperature = consigne_base
                self._last_action = f"Température {temp_piece}°C > consigne+hystérésis ({self._target_temperature+self._hysteresis}°C) - Climatisation activée à {self._target_temperature}°C"
                await self._control_minisplit()
            elif temp_piece <= self._target_temperature - self._offset:
                # Consigne atteinte - offset - passer en repli
                self._target_temperature = consigne_base + self._offset
                self._last_action = f"Consigne atteinte-offset ({temp_piece}°C) - Repli à {self._target_temperature}°C pour économie d'énergie"
                await self._control_minisplit()

    async def _control_minisplit(self):
        """Contrôler le mini-split réel"""
        mini_split_entity = self._config.get(CONF_MINI_SPLIT)
        if not mini_split_entity:
            return

        # Récupérer l'état actuel du mini-split
        mini_split_state = self.hass.states.get(mini_split_entity)
        if not mini_split_state:
            return

        self._minisplit_target = mini_split_state.attributes.get("temperature")
        self._minisplit_mode = mini_split_state.state

        # Arrêt du mini-split
        if self._hvac_mode == HVACMode.OFF:
            await self.hass.services.async_call(
                "climate",
                "set_hvac_mode",
                {"entity_id": mini_split_entity, "hvac_mode": "off"},
                blocking=True,
            )
            _LOGGER.info(f"Mini-split arrêté")
            return

        # Conversion du mode
        hvac_mode_map = {
            HVACMode.HEAT: "heat",
            HVACMode.COOL: "cool",
            HVACMode.AUTO: "auto",
        }
        
        mini_split_mode = hvac_mode_map.get(self._hvac_mode, "auto")

        # Changer le mode si nécessaire
        if self._minisplit_mode != mini_split_mode:
            await self.hass.services.async_call(
                "climate",
                "set_hvac_mode",
                {"entity_id": mini_split_entity, "hvac_mode": mini_split_mode},
                blocking=True,
            )
            _LOGGER.info(f"Mode mini-split changé vers {mini_split_mode}")

        # Changer la température si nécessaire
        if self._target_temperature and (
            self._minisplit_target is None or 
            abs(self._minisplit_target - self._target_temperature) > 0.5
        ):
            await self.hass.services.async_call(
                "climate",
                "set_temperature",
                {
                    "entity_id": mini_split_entity,
                    "temperature": self._target_temperature,
                },
                blocking=True,
            )
            _LOGGER.info(f"Consigne mini-split changée à {self._target_temperature}°C")
