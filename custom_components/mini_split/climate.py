"""Capteur de climatisation pour Mini-Split"""

import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT, HVAC_MODE_OFF, HVAC_MODE_AUTO,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_FAN_MODE
)
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configuration depuis la configuration YAML"""
    async_add_entities([MiniSplitClimate(hass, config)], True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration depuis une entrée de configuration"""
    config = config_entry.data
    async_add_entities([MiniSplitClimate(hass, config)], True)

class MiniSplitClimate(ClimateEntity):
    """Représentation d'un mini-split avec logique avancée"""

    def __init__(self, hass, config):
        self.hass = hass
        self._config = config
        self._name = "Mini-Split"
        self._current_temperature = None
        self._target_temperature = None
        self._hvac_mode = HVAC_MODE_OFF
        self._hysteresis = config.get("hysteresis", 2)
        self._repli = config.get("repli", 1)  # Valeur de repli pour réduction de consigne
        self._season = "été"  # Par défaut
        self._manual_mode = False  # Mode manuel détecté

    @property
    def name(self):
        """Nom de l'appareil"""
        return self._name

    @property
    def temperature_unit(self):
        """Unité de température"""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Température actuelle"""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Température cible"""
        return self._target_temperature

    @property
    def hvac_mode(self):
        """Mode HVAC"""
        return self._hvac_mode

    @property
    def supported_features(self):
        """Fonctionnalités supportées"""
        return SUPPORT_TARGET_TEMPERATURE

    async def async_set_temperature(self, **kwargs):
        """Définir la température avec détection mode manuel"""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            # Détecter le mode manuel
            self._manual_mode = True
            self._target_temperature = temperature
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Définir le mode HVAC avec détection mode manuel"""
        self._manual_mode = True
        self._hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_update(self):
        """Mise à jour de l'état avec logique avancée"""
        # Récupérer les données des capteurs avec gestion d'erreur
        temp_ext = self.hass.states.get(self._config.get("temperature_exterieure"))
        temp_piece = self.hass.states.get(self._config.get("temperature_piece"))
        
        # Gestion des capteurs manquants
        temp_ext_value = 15.0  # Valeur par défaut
        temp_piece_value = 20.0  # Valeur par défaut
        
        if temp_ext:
            try:
                temp_ext_value = float(temp_ext.state)
                self._current_temperature = temp_ext_value
                # Déterminer la saison
                self._season = "hiver" if temp_ext_value < 10 else "été"
            except (ValueError, TypeError):
                temp_ext_value = 15.0
                
        if temp_piece:
            try:
                temp_piece_value = float(temp_piece.state)
            except (ValueError, TypeError):
                temp_piece_value = 20.0
        
        # Vérifier si on est en mode manuel via le capteur climate direct
        climate_entity = self._config.get("mini_split_climate")
        if climate_entity:
            climate_state = self.hass.states.get(climate_entity)
            if climate_state:
                # Vérifier si l'utilisateur a modifié directement
                current_temp = climate_state.attributes.get('temperature')
                if current_temp and self._target_temperature and abs(current_temp - self._target_temperature) > 0.5:
                    self._manual_mode = True
                    
        # Logique de présence et de mode
        presence_piece = self.hass.states.get(self._config.get("presence_piece"))
        presence_maison = self.hass.states.get(self._config.get("presence_maison"))
        
        # Gestion des capteurs de présence manquants
        if presence_maison is None:
            # Si pas de capteur maison, on considère que la maison est présente
            presence_maison_state = "on"
        else:
            presence_maison_state = presence_maison.state if presence_maison.state else "on"
            
        if presence_piece is None:
            # Si pas de capteur pièce, on considère que la pièce est présente
            presence_piece_state = "on"
        else:
            presence_piece_state = presence_piece.state if presence_piece.state else "on"
        
        # Mode manuel détecté
        if self._manual_mode:
            # Désactivation automatique du mode manuel uniquement quand la maison est vide
            if presence_maison_state == "off":
                self._manual_mode = False
        else:
            # Logique de présence
            if presence_maison_state == "off":
                # Maison vide - arrêt complet
                self._hvac_mode = HVAC_MODE_OFF
                self._target_temperature = None
            elif presence_piece_state == "off":
                # Pièce vide - mode ÉCO
                self._set_eco_mode()
            else:
                # Pièce présente - mode CONFOR
                self._set_comfort_mode()
        
        # Logique de hystérésis avancée
        self._apply_hysteresis_logic()

    def _set_eco_mode(self):
        """Définir le mode ÉCO selon la saison"""
        if self._season == "hiver":
            # Mode chauffage ÉCO
            self._hvac_mode = HVAC_MODE_HEAT
            self._target_temperature = self._config.get("consigne_eco_chauffage", 20)
        else:
            # Mode climatisation ÉCO
            self._hvac_mode = HVAC_MODE_AUTO
            self._target_temperature = self._config.get("consigne_eco_climatisation", 25)

    def _set_comfort_mode(self):
        """Définir le mode CONFOR selon la saison"""
        if self._season == "hiver":
            # Mode chauffage CONFOR
            self._hvac_mode = HVAC_MODE_HEAT
            self._target_temperature = self._config.get("consigne_confort_chauffage", 22)
        else:
            # Mode climatisation CONFOR
            self._hvac_mode = HVAC_MODE_AUTO
            self._target_temperature = self._config.get("consigne_confort_climatisation", 24)

    def _apply_hysteresis_logic(self):
        """Appliquer la logique d'hystérésis avancée"""
        if self._target_temperature is None:
            return
            
        temp_piece = self.hass.states.get(self._config.get("temperature_piece"))
        if temp_piece:
            try:
                current_temp = float(temp_piece.state)
                
                # Mode chauffage
                if self._hvac_mode == HVAC_MODE_HEAT:
                    if current_temp < self._target_temperature - self._hysteresis:
                        # Activer le chauffage
                        pass
                    elif current_temp > self._target_temperature + self._hysteresis:
                        # Désactiver le chauffage
                        pass
                    elif current_temp >= self._target_temperature and self._target_temperature > self._config.get("consigne_confort_chauffage", 22):
                        # Réduire la consigne pour économiser
                        self._target_temperature = self._target_temperature - self._repli
                        
                # Mode climatisation
                elif self._hvac_mode == HVAC_MODE_AUTO:
                    if current_temp > self._target_temperature + self._hysteresis:
                        # Activer le refroidissement
                        pass
                    elif current_temp < self._target_temperature - self._hysteresis:
                        # Désactiver le refroidissement
                        pass
                    elif current_temp <= self._target_temperature and self._target_temperature < self._config.get("consigne_confort_climatisation", 24):
                        # Réduire la consigne pour économiser
                        self._target_temperature = self._target_temperature + self._repli
            except (ValueError, TypeError):
                # En cas d'erreur de lecture de température, on ne fait rien
                pass
