"""Constantes pour l'intégration Mini-Split"""

DOMAIN = "mini_split"
PLATFORMS = ["climate", "sensor", "switch"]
DEFAULT_NAME = "Mini-Split"
DEFAULT_HYSTERESIS = 2
DEFAULT_OFFSET = 1
DEFAULT_CONSIGNES = {
    "absence": {"chauffage": 18, "climatisation": 26},
    "eco": {"chauffage": 20, "climatisation": 25},
    "confort": {"chauffage": 22, "climatisation": 24}
}
