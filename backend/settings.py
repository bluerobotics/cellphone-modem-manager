from typing import Any, Dict, List, Tuple

from pydantic import BaseModel

from commonwealth.settings.settings import PydanticSettings

class CellLocationSettings(BaseModel):
    latitude: float
    longitude: float
    range: int


class DataUsageSettings(BaseModel):
    def total_data_used(self) -> int:
        return self.data_used[0] + self.data_used[1]

    # Data limit in bytes, default is 2GB
    data_limit: int = 2 * 1024 * 1024 * 1024
    # The day of the month when the data usage resets
    data_reset_day: int = 1
    # RX and TX data used in bytes
    data_used: Tuple[int, int] = (0, 0)
    # List of data points from last data_reset_day to now, key is the month day and value is RX and TX data used
    data_points: Dict[int, Tuple[int, int]] = {}


class ModemsSettings(BaseModel):
    identifier: str
    configured: bool
    data_usage: DataUsageSettings


class SettingsV1(PydanticSettings):
    # We store seen cells in dict with keys mcc, mnc, lac, cell_id
    seen_cells: Dict[int, Dict[int, Dict[int, Dict[int, CellLocationSettings]]]] = {}
    modems: Dict[str, ModemsSettings] = {}

    def migrate(self, data: Dict[str, Any]) -> None:
        if data["VERSION"] == SettingsV1.STATIC_VERSION:
            return

        if data["VERSION"] < SettingsV1.STATIC_VERSION:
            super().migrate(data)

        data["VERSION"] = SettingsV1.STATIC_VERSION
