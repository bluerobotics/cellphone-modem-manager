from typing import Any, Dict, List, Optional, cast

import aiohttp

from commonwealth.settings.manager import PydanticManager
from commonwealth.utils.Singleton import Singleton

from cells.models import NearbyCellTower, NearbyCellRadio
from config import SERVICE_NAME
from settings import SettingsV1, CellLocationSettings


class CellFetcher(metaclass=Singleton):
    _manager: PydanticManager = PydanticManager(SERVICE_NAME, SettingsV1)

    @property
    def _settings(self) -> SettingsV1:
        return cast(SettingsV1, self._manager.settings)

    def add_to_cache(self, mcc: int, mnc: int, lac: int, cell_id: int, location: CellLocationSettings) -> None:
        current: Dict = self._settings.seen_cells
        for key in [ mcc, mnc, lac ]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[cell_id] = location

        self._manager.save()

    def fetch_from_cache(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocationSettings]:
        current: Any = self._settings.seen_cells
        for key in [ mcc, mnc, lac, cell_id ]:
            if current is None:
                return None
            current = current.get(key)

        return cast(CellLocationSettings, current)

    async def fetch_from_api(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocationSettings]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://opencellid.org/ajax/searchCell.php?mcc={mcc}&mnc={mnc}&lac={lac}&cell_id={cell_id}"
                ) as resp:
                    resp.raise_for_status()

                    data = await resp.json()

                    return CellLocationSettings(
                        latitude=data["lat"],
                        longitude=data["lon"],
                        range=data["range"]
                    )
        except Exception:
            return None

    async def fetch_nearby_from_api(self, x1: float, x2: float, y1: float, y2: float) -> List[NearbyCellTower]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://opencellid.org/ajax/getCells.php?bbox={x1},{y1},{x2},{y2}"
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

                    if (data["type"] == "FeatureCollection"):
                        return [
                            NearbyCellTower(
                                latitude=feature["geometry"]["coordinates"][1],
                                longitude=feature["geometry"]["coordinates"][0],
                                range=feature["properties"]["range"],
                                radio=NearbyCellRadio(type=feature["properties"]["radio"])
                            ) for feature in data["features"]
                            if (feature["geometry"]["type"] == "Point")
                        ]
        except Exception:
            return []

    async def fetch_and_add(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocationSettings]:
        location: CellLocationSettings = await self.fetch_from_api(mcc, mnc, lac, cell_id)
        if location is not None:
            self.add_to_cache(mcc, mnc, lac, cell_id, location)
        return location

    async def fetch_cell(self, mcc: int, mnc: int, lac: int, cell_id: int) -> Optional[CellLocationSettings]:
        return self.fetch_from_cache(mcc, mnc, lac, cell_id) or await self.fetch_and_add(mcc, mnc, lac, cell_id)

    async def fetch_nearby_cells(self, lat: float, lon: float, range: float = 0.01) -> List[NearbyCellTower]:
        return await self.fetch_nearby_from_api(lon - range, lon + range, lat - range, lat + range)
