"""Data models for the PVPC España integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class Zone(StrEnum):
    """Supported PVPC zones."""

    PENINSULA = "peninsula"
    CANARIAS = "canarias"
    BALEARES = "baleares"
    CEUTA = "ceuta"
    MELILLA = "melilla"

    @property
    def api_name(self) -> str:
        """Return the ESIOS API zone name."""

        return {
            Zone.PENINSULA: "Península",
            Zone.CANARIAS: "Canarias",
            Zone.BALEARES: "Baleares",
            Zone.CEUTA: "Ceuta",
            Zone.MELILLA: "Melilla",
        }[self]


@dataclass(slots=True, frozen=True)
class PVPCHour:
    """Price for one hour."""

    start: datetime
    end: datetime
    price: float

    @property
    def hour(self) -> int:
        """Return hour number."""
        return self.start.hour


@dataclass(slots=True)
class PVPCDay:
    """Prices for one day."""

    date: date
    zone: Zone
    hours: list[PVPCHour]

    @property
    def current_hour(self) -> PVPCHour | None:
        """Return current hour."""

        now = datetime.now().astimezone()

        for hour in self.hours:
            if hour.start <= now < hour.end:
                return hour

        return None

    @property
    def next_hour(self) -> PVPCHour | None:
        """Return next hour."""

        now = datetime.now().astimezone()

        future = [
            hour
            for hour in self.hours
            if hour.start > now
        ]

        return min(future, key=lambda h: h.start) if future else None

    @property
    def min_hour(self) -> PVPCHour:
        """Return cheapest hour."""

        return min(self.hours, key=lambda h: h.price)

    @property
    def max_hour(self) -> PVPCHour:
        """Return most expensive hour."""

        return max(self.hours, key=lambda h: h.price)

    @property
    def min_price(self) -> float:
        """Return minimum price."""

        return self.min_hour.price

    @property
    def max_price(self) -> float:
        """Return maximum price."""

        return self.max_hour.price

    @property
    def average_price(self) -> float:
        """Return average price."""

        return sum(h.price for h in self.hours) / len(self.hours)

    @property
    def remaining_hours(self) -> list[PVPCHour]:
        """Return remaining hours."""

        now = datetime.now().astimezone()

        return [
            hour
            for hour in self.hours
            if hour.end > now
        ]

    @property
    def remaining_average(self) -> float | None:
        """Return remaining average price."""

        hours = self.remaining_hours

        if not hours:
            return None

        return sum(h.price for h in hours) / len(hours)


@dataclass(slots=True)
class PVPCResponse:
    """Complete API response."""

    today: PVPCDay
    tomorrow: PVPCDay | None = None