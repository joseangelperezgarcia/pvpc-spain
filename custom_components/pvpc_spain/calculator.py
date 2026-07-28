"""PVPC calculation helpers.

Business logic for PVPC España integration.
This module works with PVPCResponse models and
does not contain Home Assistant specific code.
"""

from __future__ import annotations
from homeassistant.util import dt as dt_util
from datetime import datetime
from typing import Any
from .models import PVPCDay, PVPCResponse
from .holidays import is_national_holiday

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def _round(
    value: float | None,
    decimals: int = 5,
) -> float | None:
    """Round numeric values safely."""

    if value is None:
        return None

    return round(value, decimals)


def _hour_to_dict(hour) -> dict[str, Any]:
    """Convert a PVPCHour into an attribute-friendly dict."""

    return {
        "hour": hour.hour,
        "start": hour.start.isoformat(),
        "end": hour.end.isoformat(),
        "price": _round(hour.price),
    }


def _hours_to_list(
    day: PVPCDay | None,
) -> list[dict[str, Any]]:
    """Convert daily hours to dictionaries."""

    if day is None:
        return []

    return [
        _hour_to_dict(hour)
        for hour in day.hours
    ]


# -------------------------------------------------------------------
# Current prices
# -------------------------------------------------------------------


def current_price(
    data: PVPCResponse,
) -> float | None:
    """Return current PVPC price."""

    hour = data.today.current_hour

    if hour is None:
        return None

    return _round(hour.price)


def next_price(
    data: PVPCResponse,
) -> float | None:
    """Return next hour price."""

    hour = data.today.next_hour

    if hour is None:
        return None

    return _round(hour.price)


# -------------------------------------------------------------------
# Today statistics
# -------------------------------------------------------------------

def today_prices(data: PVPCResponse) -> float | None:
    """Return current price for today."""

    current = current_hour(data)

    if current is None:
        return None

    return current.price

def today_current_price(data: PVPCResponse) -> float | None:
    """Return current hour price."""

    now = dt_util.now()

    for hour in data.today.hours:
        if hour.start <= now < hour.end:
            return hour.price

    return None

def get_today_prices(data: PVPCResponse) -> dict[str, dict[str, Any]]:
    """Return today's prices with tariff period."""

    prices = {}

    for hour in data.today.hours:
        time = hour.start.strftime("%H:%M")

        prices[time] = {
            "price": hour.price,
            "period": tariff_period_for_hour(
                hour.start
            ),
        }

    return prices

def tariff_period_for_hour(dt) -> str:
    """Return PVPC 2.0TD period for a datetime."""

    if dt.weekday() >= 5:
        return "Valle"

    if is_national_holiday(dt.date()):
        return "Valle"

    hour = dt.hour

    if 0 <= hour < 8:
        return "Valle"

    if (
        8 <= hour < 10
        or 14 <= hour < 18
        or 22 <= hour < 24
    ):
        return "Llano"

    return "Punta"

def minimum_price(
    data: PVPCResponse,
) -> float:
    """Return today's minimum price."""

    return _round(
        data.today.min_price
    )


def maximum_price(
    data: PVPCResponse,
) -> float:
    """Return today's maximum price."""

    return _round(
        data.today.max_price
    )


def average_price(
    data: PVPCResponse,
) -> float:
    """Return today's average price."""

    return _round(
        data.today.average_price
    )


def cheapest_hour(
    data: PVPCResponse,
) -> int:
    """Return cheapest hour number."""

    return data.today.min_hour.hour


def expensive_hour(
    data: PVPCResponse,
) -> int:
    """Return most expensive hour number."""

    return data.today.max_hour.hour


# -------------------------------------------------------------------
# Remaining day
# -------------------------------------------------------------------


def remaining_hours(
    data: PVPCResponse,
) -> int:
    """Return remaining hours count."""

    return len(
        data.today.remaining_hours
    )


def remaining_average(
    data: PVPCResponse,
) -> float | None:
    """Return remaining hours average price."""

    return _round(
        data.today.remaining_average
    )


# -------------------------------------------------------------------
# Price analysis
# -------------------------------------------------------------------


def price_class(
    data: PVPCResponse,
) -> str | None:
    """
    Classify current price.

    Returns:
        Muy barato
        Barato
        Normal
        Caro
        Muy caro
    """

    current = current_price(data)

    if current is None:
        return None

    average = data.today.average_price

    if average == 0:
        return None

    ratio = current / average

    if ratio < 0.70:
        return "Muy barato"

    if ratio < 0.90:
        return "Barato"

    if ratio < 1.10:
        return "Normal"

    if ratio < 1.30:
        return "Caro"

    return "Muy caro"


def current_rank(
    data: PVPCResponse,
) -> int | None:
    """
    Return current hour ranking.

    1 = cheapest
    24 = most expensive
    """

    current = data.today.current_hour

    if current is None:
        return None

    sorted_hours = sorted(
        data.today.hours,
        key=lambda hour: hour.price,
    )

    for index, hour in enumerate(
        sorted_hours,
        start=1,
    ):
        if hour.start == current.start:
            return index

    return None


def difference_from_average(
    data: PVPCResponse,
) -> float | None:
    """Return current price difference percentage."""

    current = current_price(data)

    if current is None:
        return None

    average = data.today.average_price

    if average == 0:
        return None

    return round(
        ((current - average) / average) * 100,
        2,
    )


# -------------------------------------------------------------------
# Tomorrow
# -------------------------------------------------------------------


def tomorrow_minimum(
    data: PVPCResponse,
) -> float | None:
    """Return tomorrow minimum price."""

    if data.tomorrow is None:
        return None

    return _round(
        data.tomorrow.min_price
    )


def tomorrow_maximum(
    data: PVPCResponse,
) -> float | None:
    """Return tomorrow maximum price."""

    if data.tomorrow is None:
        return None

    return _round(
        data.tomorrow.max_price
    )


def tomorrow_average(
    data: PVPCResponse,
) -> float | None:
    """Return tomorrow average price."""

    if data.tomorrow is None:
        return None

    return _round(
        data.tomorrow.average_price
    )


def tomorrow_cheapest_hour(
    data: PVPCResponse,
) -> int | None:
    """Return tomorrow cheapest hour."""

    if data.tomorrow is None:
        return None

    return data.tomorrow.min_hour.hour


def tomorrow_expensive_hour(
    data: PVPCResponse,
) -> int | None:
    """Return tomorrow expensive hour."""

    if data.tomorrow is None:
        return None

    return data.tomorrow.max_hour.hour


# -------------------------------------------------------------------
# Attributes
# -------------------------------------------------------------------


def get_price_summary(
    data: PVPCResponse,
) -> dict[str, Any]:
    """
    Return attributes for main sensor.
    """

    return {
        "today_prices": _hours_to_list(
            data.today
        ),

        "tomorrow_prices": _hours_to_list(
            data.tomorrow
        ),

        "minimum_price": minimum_price(data),
        "minimum_hour": cheapest_hour(data),

        "maximum_price": maximum_price(data),
        "maximum_hour": expensive_hour(data),

        "average_price": average_price(data),

        "remaining_average": remaining_average(data),

        "zone": data.today.zone.value,

        "last_update": datetime.now().astimezone().isoformat(),
    }


# Vacaciones o no para t horario

def tariff_period(data: PVPCResponse) -> str:
    """Return current 2.0TD tariff period."""

    now = dt_util.now()

    if now.weekday() >= 5:
        return "Valle"

    if is_national_holiday(now.date()):
        return "Valle"

    hour = now.hour

    if 0 <= hour < 8:
        return "Valle"

    if (
        8 <= hour < 10
        or 14 <= hour < 18
        or 22 <= hour < 24
    ):
        return "Llano"

    return "Punta"