"""API client for PVPC España."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from aiohttp import ClientError, ClientSession
from homeassistant.util import dt as dt_util

from .models import (
    PVPCHour,
    PVPCDay,
    PVPCResponse,
    Zone,
)


API_URL = (
    "https://api.esios.ree.es/indicators/1001"
)


class PVPCApiError(Exception):
    """PVPC API error."""


class PVPCApi:
    """PVPC API client."""

    def __init__(
        self,
        session: ClientSession,
        token: str,
    ) -> None:
        """Initialize API."""

        self._session = session
        self._token = token

    @property
    def headers(self) -> dict[str, str]:
        """Return request headers."""

        return {
            "Accept": (
                "application/json; "
                "application/vnd.esios-api-v2+json"
            ),
            "Content-Type": "application/json",
            "Authorization": (
                f'Token token="{self._token}"'
            ),
        }

    async def async_get_prices(
        self,
        zone: Zone,
    ) -> PVPCResponse:
        """Return PVPC prices."""

        payload = await self._download()

        return self._parse(
            payload,
            zone,
        )

    async def _download(self) -> dict[str, Any]:
        """Download API data."""

        try:
            async with self._session.get(
                API_URL,
                headers=self.headers,
                timeout=30,
            ) as response:

                response.raise_for_status()

                return await response.json()

        except ClientError as err:
            raise PVPCApiError(
                str(err)
            ) from err

    def _parse(
        self,
        payload: dict[str, Any],
        zone: Zone,
    ) -> PVPCResponse:
        """Parse API response."""

        try:
            values = (
                payload["indicator"]["values"]
            )

        except KeyError as err:
            raise PVPCApiError(
                "Invalid API response format"
            ) from err

        grouped: dict[
            date,
            list[PVPCHour],
        ] = defaultdict(list)

        for item in values:

            if item.get("geo_name") != zone.api_name:
                continue

            start_raw = item.get("datetime")

            if not isinstance(start_raw, str):
                continue

            start = dt_util.parse_datetime(start_raw)

            if start is None:
                continue

            end_raw = item.get("datetime_end")

            if isinstance(end_raw, str):
                end = dt_util.parse_datetime(end_raw)
            else:
                end = None

            if end is None:
                end = start + timedelta(hours=1)

            try:
                price = float(item["value"]) / 1000

            except (KeyError, TypeError, ValueError):
                continue

            grouped[start.date()].append(
                PVPCHour(
                    start=start,
                    end=end,
                    price=price,
                )
            )

        if not grouped:
            raise PVPCApiError(
                f"No data found for zone {zone.api_name}"
            )

        days = [
            PVPCDay(
                date=day,
                zone=zone,
                hours=sorted(
                    hours,
                    key=lambda hour: hour.start,
                ),
            )
            for day, hours in sorted(
                grouped.items()
            )
        ]

        return PVPCResponse(
            today=days[0],
            tomorrow=(
                days[1]
                if len(days) > 1
                else None
            ),
        )