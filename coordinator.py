"""DataUpdateCoordinator for PVPC España."""

from __future__ import annotations

import logging

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import PVPCApi, PVPCApiError
from .const import CONF_TOKEN, CONF_ZONE, DOMAIN, UPDATE_INTERVAL
from .models import PVPCResponse, Zone

_LOGGER = logging.getLogger(__name__)


class PVPCCoordinator(DataUpdateCoordinator[PVPCResponse]):
    """Coordinator for PVPC España."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""

        self.config_entry = entry

        session: ClientSession = async_get_clientsession(hass)

        self.api = PVPCApi(
            session=session,
            token=entry.data[CONF_TOKEN],
        )

        self.zone = Zone(entry.data[CONF_ZONE])

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> PVPCResponse:
        """Fetch data from the API."""

        try:
            return await self.api.async_get_prices(self.zone)

        except PVPCApiError as err:
            raise UpdateFailed(str(err)) from err