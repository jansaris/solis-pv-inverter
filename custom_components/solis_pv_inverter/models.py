"""Models for the Solis PV Inverter integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription


@dataclass
class SolisSensorEntityDescription(SensorEntityDescription):
    """Sensor entity description for Solis PV Inverter."""

    api_key: str | None = None
