"""Config flow for Solis PV Converter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .solis import Solis

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solis PV Inverter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Start config flow")
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await ConfigFlow.validate_input(user_input)
            user_input[CONF_NAME] = "Solis PV Inverter"
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        if user_input is None or errors:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

    @staticmethod
    async def validate_input(data: dict[str, Any]):
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        _LOGGER.debug("Start validating user input")
        hub = Solis(data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD])
        result = await hub.retrieve()

        if not result.reachable:
            _LOGGER.debug("Form invalid because Solis PV Inverter not reachable")
            raise CannotConnect(result.status)

        if result.http_code == 401:
            _LOGGER.debug(
                "Form invalid because Solis PV Inverter credentials are not ok"
            )
            raise InvalidAuth

        if result.error:
            _LOGGER.debug(
                "Form invalid because Solis PV Inverter returned an error: %s",
                result.status,
            )
            raise CannotConnect(result.status)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
