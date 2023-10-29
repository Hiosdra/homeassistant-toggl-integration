"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    TogglApiClient,
    TogglApiClientAuthenticationError,
    TogglApiClientCommunicationError,
    TogglApiClientError,
)
from .const import DOMAIN, LOGGER


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    api_token=user_input[CONF_API_KEY],
                )
            except TogglApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except TogglApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except TogglApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_API_KEY],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY,
                        default=(user_input or {}).get(CONF_API_KEY),
                    ): str,
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, api_token: str) -> None:
        """Validate credentials."""
        client = TogglApiClient(
            api_token=api_token,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
