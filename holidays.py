"""Spanish holidays helper."""

from datetime import date

import holidays


ES_HOLIDAYS = holidays.Spain()


def is_national_holiday(day: date) -> bool:
    """Return if day is a Spanish national holiday."""

    return day in ES_HOLIDAYS