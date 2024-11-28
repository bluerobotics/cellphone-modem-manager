from enum import StrEnum
from typing import Any, Dict, Optional

import aiohttp

from config import MAV_LINK_2_REST_API
from utils import string_to_unicode_array


class MAVSeverity(StrEnum):
    EMERGENCY = "MAV_SEVERITY_EMERGENCY"
    ALERT = "MAV_SEVERITY_ALERT"
    CRITICAL = "MAV_SEVERITY_CRITICAL"
    ERROR = "MAV_SEVERITY_ERROR"
    WARNING = "MAV_SEVERITY_WARNING"
    NOTICE = "MAV_SEVERITY_NOTICE"
    INFO = "MAV_SEVERITY_INFO"
    DEBUG = "MAV_SEVERITY_DEBUG"


class MAVLink2Rest:
    api_url = f"{MAV_LINK_2_REST_API}/mavlink"

    @staticmethod
    def _get_default_header() -> Dict:
        return {
            "system_id": 255,
            "component_id": 0,
            "sequence": 0
        }

    @staticmethod
    async def _post_data(data: Any) -> None:
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            async with session.post(MAVLink2Rest.api_url, json=data, headers=headers) as resp:
                resp.raise_for_status()

    @classmethod
    async def send_status_text(cls, text: str, severity: MAVSeverity) -> None:
        data = {
            "header": cls._get_default_header(),
            "message": {
                "type": "STATUSTEXT",
                "severity": {
                    "type": severity
                },
                "text": string_to_unicode_array(text, 50),
                "id": 0,
                "chunk_seq": 0
            }
        }
        await cls._post_data(data)

    @classmethod
    async def send_named_float(cls, name: str, value: float) -> None:
        data = {
            "header": cls._get_default_header(),
            "message": {
                "type": "NAMED_VALUE_FLOAT",
                "time_boot_ms": 0,
                "value": value,
                "name": string_to_unicode_array(name, 10)
            }
        }
        await cls._post_data(data)

    @classmethod
    async def get_global_position(cls) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Accept": "application/json"}
                async with session.get(MAVLink2Rest.api_url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

                    # If some data is missing, will return None
                    return data["vehicles"]["1"]["components"]["1"]["messages"]["GLOBAL_POSITION_INT"]["message"]
        except Exception:
            return None
