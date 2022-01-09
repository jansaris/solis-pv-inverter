"""Read status of Solis PV Inverter."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
    POWER_WATT,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import Throttle

from .const import DOMAIN, SCAN_INTERVAL
from .models import SolisSensorEntityDescription
from .solis import Solis

_LOGGER = logging.getLogger(__name__)

# Supported overview sensors
SENSOR_TYPES = [
    SolisSensorEntityDescription(
        key="lifetime_energy",
        api_key="yield_total",
        name="Lifetime energy",
        icon="mdi:solar-power",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SolisSensorEntityDescription(
        key="energy_today",
        api_key="yield_tody",
        name="Energy today",
        icon="mdi:solar-power",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SolisSensorEntityDescription(
        key="current_power",
        api_key="current_power",
        name="Current Power",
        icon="mdi:solar-power",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SolisSensorEntityDescription(
        key="current_power_kw",
        api_key="current_power_kw",
        name="Current Power kW",
        icon="mdi:solar-power",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=POWER_KILO_WATT,
        device_class=SensorDeviceClass.POWER,
    ),
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Solis PV Inverter sensors."""
    config = config_entry.data

    api = Solis(config[CONF_HOST], config[CONF_USERNAME], config[CONF_PASSWORD])

    entities = [
        SolisInverterEntity(
            api,
            config[CONF_NAME],
            description=description,
        )
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities, True)


class SolisInverterEntity(SensorEntity):
    """Representation of a Solis PV Inverter Sensor."""

    entity_description: SolisSensorEntityDescription

    def __init__(
        self, api: Solis, device_name, description: SolisSensorEntityDescription
    ):
        """Initialize a Solis PV Inverter sensor."""
        self.api = api
        self.entity_description = description

        self._attr_name = description.name
        self._attr_unique_id = description.key
        self._attr_icon = description.icon
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        # First async update will make the sensor to available
        self._attr_available = False

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_name)},
            manufacturer="Ginlong Technologies",
            name=device_name,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.api.get_value(self.entity_description.api_key)

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Get the latest data from the Solis PV Inverter and updates the state."""
        _LOGGER.debug(
            "Retrieve latest data from Solis PV Inverter for %s",
            self.entity_description.name,
        )
        model = await self.api.retrieve()
        self._attr_available = model.available
