"""Config flow for the PVPC España integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from aiohttp import ClientSession

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import PVPCApi, PVPCApiError
from .const import (
    CONF_TOKEN,
    CONF_ZONE,
    DOMAIN,
    ZONES,
)
from .models import Zone


_LOGGER = logging.getLogger(__name__)


class PVPCSpainConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for PVPC España."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            session: ClientSession = (
                async_get_clientsession(self.hass)
            )

            api = PVPCApi(
                session=session,
                token=user_input[CONF_TOKEN],
            )

            try:
                await api.async_get_prices(
                    Zone(user_input[CONF_ZONE]),
                )

            except PVPCApiError as err:
                _LOGGER.warning(
                    "PVPC API validation failed: %s",
                    err,
                )

                errors["base"] = "cannot_connect"

            except Exception as err:
                _LOGGER.exception(
                    "Unexpected error validating PVPC token",
                )

                errors["base"] = "unknown"

            else:
                await self.async_set_unique_id(
                    f"pvpc_spain_{user_input[CONF_ZONE]}"
                )

                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=(
                        "PVPC España "
                        f"({ZONES[user_input[CONF_ZONE]]})"
                    ),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ZONE,
                        default=Zone.PENINSULA.value,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {
                                    "value": zone.value,
                                    "label": ZONES[zone.value],
                                }
                                for zone in Zone
                            ],
                            mode="dropdown",
                        )
                    ),
                    vol.Required(
                        CONF_TOKEN,
                    ): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD,
                            autocomplete="off",
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
            "api_url": "https://api.esios.ree.es/"},
        )