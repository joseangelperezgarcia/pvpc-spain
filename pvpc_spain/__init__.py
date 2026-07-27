"""The PVPC España integration."""

from __future__ import annotations

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import PVPCCoordinator


type PVPCConfigEntry = ConfigEntry[PVPCCoordinator]


PLATFORMS: Final[list[Platform]] = [
    Platform.SENSOR,
]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up the PVPC España integration."""

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PVPCConfigEntry,
) -> bool:
    """Set up PVPC España from a config entry."""

    coordinator = PVPCCoordinator(
        hass=hass,
        entry=entry,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(
            async_update_listener
        )
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PVPCConfigEntry,
) -> bool:
    """Unload PVPC España."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )


async def async_update_listener(
    hass: HomeAssistant,
    entry: PVPCConfigEntry,
) -> None:
    """Handle options update."""

    await hass.config_entries.async_reload(
        entry.entry_id
    )