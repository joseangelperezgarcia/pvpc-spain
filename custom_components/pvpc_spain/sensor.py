"""PVPC sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import PVPCConfigEntry
from . import calculator
from .const import DOMAIN
from .coordinator import PVPCCoordinator
from .models import PVPCResponse


@dataclass(frozen=True, kw_only=True)
class PVPCSensorDescription(SensorEntityDescription):
    """Describe a PVPC sensor."""

    value_fn: Callable[[PVPCResponse], Any]


SENSORS: tuple[PVPCSensorDescription, ...] = (

    PVPCSensorDescription(
        key="current_price",
        name="Precio actual",
        icon="mdi:flash",
        value_fn=calculator.current_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="next_price",
        name="Precio siguiente hora",
        icon="mdi:clock-fast",
        value_fn=calculator.next_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="minimum_price",
        name="Precio mínimo",
        icon="mdi:arrow-down",
        value_fn=calculator.minimum_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="maximum_price",
        name="Precio máximo",
        icon="mdi:arrow-up",
        value_fn=calculator.maximum_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="average_price",
        name="Precio medio",
        icon="mdi:chart-line",
        value_fn=calculator.average_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="cheapest_hour",
        name="Hora más barata",
        icon="mdi:clock-outline",
        value_fn=calculator.cheapest_hour,
    ),

    PVPCSensorDescription(
        key="expensive_hour",
        name="Hora más cara",
        icon="mdi:clock-alert",
        value_fn=calculator.expensive_hour,
    ),

    PVPCSensorDescription(
        key="remaining_average",
        name="Precio medio restante",
        icon="mdi:chart-timeline",
        value_fn=calculator.remaining_average,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="remaining_hours",
        name="Horas restantes",
        icon="mdi:timer-outline",
        value_fn=calculator.remaining_hours,
    ),

    PVPCSensorDescription(
        key="price_class",
        name="Clasificación del precio",
        icon="mdi:information-outline",
        value_fn=calculator.price_class,
        device_class=SensorDeviceClass.ENUM,
        options=(
            "Muy barato",
            "Barato",
            "Medio",
            "Caro",
            "Muy caro",
        ),
    ),

    PVPCSensorDescription(
        key="zone",
        name="Zona",
        icon="mdi:map-marker",
        value_fn=lambda data: data.today.zone.api_name,
        device_class=SensorDeviceClass.ENUM,
        options=(
            "Península",
            "Canarias",
            "Baleares",
            "Ceuta",
            "Melilla",
        ),
    ),

    PVPCSensorDescription(
        key="tariff_period",
        name="Tramo tarifario",
        icon="mdi:calendar-clock",
        value_fn=calculator.tariff_period,
        device_class=SensorDeviceClass.ENUM,
        options=(
            "Valle",
            "Llano",
            "Punta",
        ),
    ),

    PVPCSensorDescription(
        key="current_rank",
        name="Ranking hora actual",
        icon="mdi:sort-numeric-ascending",
        value_fn=calculator.current_rank,
    ),

    PVPCSensorDescription(
        key="difference_from_average",
        name="Diferencia respecto a la media",
        icon="mdi:percent",
        value_fn=calculator.difference_from_average,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
    ),

    PVPCSensorDescription(
        key="tomorrow_minimum",
        name="Precio mañana mínimo",
        icon="mdi:arrow-down",
        value_fn=calculator.tomorrow_minimum,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="tomorrow_maximum",
        name="Precio mañana máximo",
        icon="mdi:arrow-up",
        value_fn=calculator.tomorrow_maximum,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="today_prices",
        name="Precio hoy",
        icon="mdi:chart-line",
        value_fn=calculator.today_current_price,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="tomorrow_average",
        name="Precio mañana medio",
        icon="mdi:chart-line",
        value_fn=calculator.tomorrow_average,
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),

    PVPCSensorDescription(
        key="tomorrow_cheapest_hour",
        name="Hora más barata mañana",
        icon="mdi:clock-outline",
        value_fn=calculator.tomorrow_cheapest_hour,
    ),

    PVPCSensorDescription(
        key="tomorrow_expensive_hour",
        name="Hora más cara mañana",
        icon="mdi:clock-alert",
        value_fn=calculator.tomorrow_expensive_hour,
    ),
)


async def async_setup_entry(
    hass,
    entry: PVPCConfigEntry,
    async_add_entities,
) -> None:
    """Set up PVPC sensors."""

    coordinator: PVPCCoordinator = entry.runtime_data

    async_add_entities(
        [
            PVPCSensor(
                coordinator,
                description,
            )
            for description in SENSORS
        ],
        update_before_add=True,
    )


class PVPCSensor(
    CoordinatorEntity[PVPCCoordinator],
    SensorEntity,
):
    """Representation of a PVPC sensor."""

    entity_description: PVPCSensorDescription

    def __init__(
        self,
        coordinator: PVPCCoordinator,
        description: PVPCSensorDescription,
    ) -> None:
        """Initialize sensor."""

        super().__init__(coordinator)

        self.entity_description = description

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"{description.key}"
        )

        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return DeviceInfo(
            identifiers={
                (DOMAIN, "pvpc")
            },
            name="PVPC España",
            manufacturer="PVPC España",
            model="Precio Voluntario para el Pequeño Consumidor",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        """Return sensor value."""

        return self.entity_description.value_fn(
            self.coordinator.data
        )

    @property
    def extra_state_attributes(
        self,
    ) -> dict[str, Any] | None:
        """Return extra state attributes."""

        if self.entity_description.key == "current_price":
            return calculator.get_price_summary(
                self.coordinator.data
            )

        if self.entity_description.key == "today_prices":
            return {
                "prices": calculator.get_today_prices(
                    self.coordinator.data
                )
            }

        return None