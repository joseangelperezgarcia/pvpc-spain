"""Constants for the PVPC España integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "pvpc_spain"
DEFAULT_NAME = "PVPC España"

# Config Entry
CONF_ZONE = "zone"
CONF_TOKEN = "token"

# Coordinador
UPDATE_INTERVAL = timedelta(minutes=5)

# Zonas disponibles
ZONE_PENINSULA = "peninsula"
ZONE_CANARIAS = "canarias"
ZONE_BALEARES = "baleares"
ZONE_CEUTA = "ceuta"
ZONE_MELILLA = "melilla"

ZONES = {
    ZONE_PENINSULA: "Península",
    ZONE_CANARIAS: "Canarias",
    ZONE_BALEARES: "Baleares",
    ZONE_CEUTA: "Ceuta",
    ZONE_MELILLA: "Melilla",
}