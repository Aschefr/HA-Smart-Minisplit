"""Constantes pour l'intégration HA Smart Minisplit"""

DOMAIN = "smart_minisplit"
PLATFORMS = ["climate", "sensor", "switch"]
DEFAULT_NAME = "Smart Minisplit"
DEFAULT_HYSTERESIS = 0.5
DEFAULT_OFFSET = 1.0
DEFAULT_CONSIGNES = {
    "absence": {"chauffage": 18.0, "climatisation": 26.0},
    "eco": {"chauffage": 20.0, "climatisation": 25.0},
    "confort": {"chauffage": 22.0, "climatisation": 24.0}
}

# Modes
MODE_ABSENCE = "absence"
MODE_ECO = "eco"
MODE_CONFORT = "confort"

# Saisons
SEASON_CHAUFFAGE = "chauffage"
SEASON_CLIMATISATION = "climatisation"

# États
STATE_OFF = "off"
STATE_ON = "on"
STATE_AUTO = "auto"
STATE_MANUAL = "manual"

# Attributs de configuration
CONF_MINI_SPLIT = "mini_split_climate"
CONF_TEMP_EXT = "temperature_exterieure"
CONF_TEMP_PIECE = "temperature_piece"
CONF_PRESENCE_PIECE = "presence_piece"
CONF_PRESENCE_MAISON = "presence_maison"
CONF_HYSTERESIS = "hysteresis"
CONF_OFFSET = "offset"
CONF_CONSIGNE_ABSENCE_CHAUFFAGE = "consigne_absence_chauffage"
CONF_CONSIGNE_ECO_CHAUFFAGE = "consigne_eco_chauffage"
CONF_CONSIGNE_CONFORT_CHAUFFAGE = "consigne_confort_chauffage"
CONF_CONSIGNE_ABSENCE_CLIMATISATION = "consigne_absence_climatisation"
CONF_CONSIGNE_ECO_CLIMATISATION = "consigne_eco_climatisation"
CONF_CONSIGNE_CONFORT_CLIMATISATION = "consigne_confort_climatisation"
