from typing import Any, Dict, Optional, cast

import aiohttp

from loguru import logger

from cells.models import CellLocation
from commonwealth.settings.manager import PydanticManager
from commonwealth.utils.Singleton import Singleton
from config import SERVICE_NAME
from settings import SettingsV1


class CellFetcher(metaclass=Singleton):
    _manager: PydanticManager = PydanticManager(SERVICE_NAME, SettingsV1)

    @property
    def _settings(self) -> SettingsV1:
        return cast(SettingsV1, self._manager.settings)

    def add_to_cache(self, mcc: int, mnc: int, lac: int, cell_id: int, location: CellLocation) -> None:
        current: Dict = self._settings.seen_cells
        for key in [ mcc, mnc, lac ]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[cell_id] = location

        self._manager.save()

    def fetch_from_cache(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocation]:
        current: Any = self._settings.seen_cells
        for key in [ mcc, mnc, lac, cell_id ]:
            if current is None:
                return None
            current = current.get(key)

        return cast(CellLocation, current)

    async def fetch_from_api(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocation]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://opencellid.org/ajax/searchCell.php?mcc={mcc}&mnc={mnc}&lac={lac}&cell_id={cell_id}"
                ) as resp:
                    resp.raise_for_status()

                    data = await resp.json()

                    return CellLocation(
                        latitude=data["lat"],
                        longitude=data["lon"],
                        range=data["range"]
                    )
        except Exception:
            return None

    async def fetch_and_add(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocation]:
        location: CellLocation = await self.fetch_from_api(mcc, mnc, lac, cell_id)
        if location is not None:
            self.add_to_cache(mcc, mnc, lac, cell_id, location)

        return location

    async def fetch_cell(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocation]:
        return self.fetch_from_cache(mcc, mnc, lac, cell_id) or await self.fetch_and_add(mcc, mnc, lac, cell_id)
