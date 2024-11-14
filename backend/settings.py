from typing import Any, Dict, List, Tuple

from pydantic import BaseModel

from commonwealth.settings.settings import PydanticSettings
from cells.models import CellLocation


class DataUsageSettings(BaseModel):
    data_limit: int
    # The day of the month when the data usage resets
    data_reset_day: int
    # RX and TX data used in bytes
    data_used: Tuple[int, int]
    # List of data points from last data_reset_day to now
    data_points: List[Tuple[int, int]]


class ModemsSettings(BaseModel):
    identifier: str
    configured: bool
    data_usage: DataUsageSettings


class SettingsV1(PydanticSettings):
    # We store seen cells in dict with keys mcc, mnc, lac, cell_id
    seen_cells: Dict[int, Dict[int, Dict[int, Dict[int, CellLocation]]]] = {}
    modems: Dict[str, ModemsSettings] = {}

    def migrate(self, data: Dict[str, Any]) -> None:
        if data["VERSION"] == SettingsV1.STATIC_VERSION:
            return

        if data["VERSION"] < SettingsV1.STATIC_VERSION:
            super().migrate(data)

        data["VERSION"] = SettingsV1.STATIC_VERSION