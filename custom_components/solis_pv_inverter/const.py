"""Constants for the Solis PV Inverter integration."""
from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "solis_pv_inverter"

PLATFORMS = [Platform.SENSOR]

SCAN_INTERVAL = timedelta(seconds=30)
