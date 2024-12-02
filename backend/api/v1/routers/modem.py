from functools import wraps
from typing import Any, Callable, Tuple

from fastapi import APIRouter, HTTPException, Query, status
from fastapi_versioning import versioned_api_route

from modem import Modem
from modem.exceptions import ATConnectionTimeout, InvalidModemDevice, InexistentModemPosition
from modem.models import (
    ModemCellInfo,
    ModemClockDetails,
    ModemDevice,
    ModemDeviceDetails,
    ModemPosition,
    ModemSignalQuality,
    ModemSIMStatus,
    OperatorInfo,
    PDPContext,
    USBNetMode,
)
from settings import DataUsageSettings


modem_router_v1 = APIRouter(
    prefix="/modem",
    tags=["modem_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def modem_to_http_exception(endpoint: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(endpoint)
    async def wrapper(*args: Tuple[Any], **kwargs: dict[str, Any]) -> Any:
        try:
            return await endpoint(*args, **kwargs)
        except HTTPException as error:
            raise error
        except InvalidModemDevice as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
        except InexistentModemPosition as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
        except ATConnectionTimeout as error:
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    return wrapper


@modem_router_v1.get("/", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch() -> list[ModemDevice]:
    """
    List device descriptor of all connected modems.
    """
    modems = Modem.connected_devices()
    return [
        ModemDevice(
            device=modem.device,
            id=modem.id,
            manufacturer=modem.manufacturer,
            product=modem.product
        )
        for modem in modems
    ]


@modem_router_v1.get("/{modem_id}/details", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_by_id(modem_id: str) -> ModemDeviceDetails:
    """
    Get details of a modem by id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_mt_info()


@modem_router_v1.get("/{modem_id}/signal", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_signal_strength_by_id(modem_id: str) -> ModemSignalQuality:
    """
    Get signal strength of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_signal_strength()


@modem_router_v1.get("/{modem_id}/cell", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_serving_cell_info_by_id(modem_id: str) -> ModemCellInfo:
    """
    Get serving cell and neighbors cells information of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_cell_info()


@modem_router_v1.post("/{modem_id}/commander", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def command_by_id(
    modem_id: str,
    command: str = Query(..., description="AT Command string to be executed in the modem"),
    delay: float = Query(0.3, description="Delay in seconds between command sent and response read"),
) -> None:
    """
    Execute an AT command in a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    with modem.at_commander() as cmd:
        return cmd.raw_command(
            command,
            delay=delay,
            cmd_id_response=None,
            raw_response=True,
        )


@modem_router_v1.post("/{modem_id}/reboot", status_code=status.HTTP_204_NO_CONTENT)
@modem_to_http_exception
async def reboot_by_id(modem_id: str) -> None:
    """
    Reboot a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.reboot()


@modem_router_v1.post("/{modem_id}/reset", status_code=status.HTTP_204_NO_CONTENT)
@modem_to_http_exception
async def reset_by_id(modem_id: str) -> None:
    """
    Reset a modem to factory settings by modem id. Make sure you know what you are doing.
    """
    modem = Modem.get_device(modem_id)

    return modem.factory_reset()


@modem_router_v1.get("/{modem_id}/clock", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_clock_by_id(modem_id: str) -> ModemClockDetails:
    """
    Return the current clock of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_clock()


@modem_router_v1.get("/{modem_id}/position", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_position_by_id(modem_id: str) -> ModemPosition:
    """
    Return the current position of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_position()


@modem_router_v1.get("/{modem_id}/sim_status", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_sim_status_by_id(modem_id: str) -> ModemSIMStatus:
    """
    Get SIM status of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_sim_status()


@modem_router_v1.get("/{modem_id}/config/usb_net", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_usb_mode_by_id(modem_id: str) -> USBNetMode:
    """
    Get USB mode of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_usb_net_mode()


@modem_router_v1.put("/{modem_id}/config/usb_net/{mode}", status_code=status.HTTP_204_NO_CONTENT)
@modem_to_http_exception
async def set_usb_mode_by_id(modem_id: str, mode: USBNetMode) -> None:
    """
    Set USB mode of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.set_usb_net_mode(mode)


@modem_router_v1.get("/{modem_id}/pdp", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_pdp_info_by_id(modem_id: str) -> list[PDPContext]:
    """
    Get PDP information of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_pdp_info()


@modem_router_v1.get("/{modem_id}/operator", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_operator_info_by_id(modem_id: str) -> OperatorInfo:
    """
    Get PDP information of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_operator_info()


@modem_router_v1.put("/{modem_id}/pdp/{profile}apn/{apn}", status_code=status.HTTP_204_NO_CONTENT)
@modem_to_http_exception
async def set_apn_by_profile_by_id(modem_id: str, profile: int, apn: str) -> None:
    """
    Set APN of a profile of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.set_apn(profile, apn)


@modem_router_v1.get("/{modem_id}/usage/details", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def fetch_data_usage_by_id(modem_id: str) -> DataUsageSettings:
    """
    Get data usage details of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_data_usage_details()


@modem_router_v1.put("/{modem_id}/usage/alert/{total_bytes}", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def set_data_usage_alert_by_id(modem_id: str, total_bytes: int) -> DataUsageSettings:
    """
    Set data usage alert of a modem by modem id.
    """
    modem = Modem.get_device(modem_id)

    return modem.set_data_usage_alert(total_bytes)


@modem_router_v1.put("/{modem_id}/usage/reset/{month_day}", status_code=status.HTTP_200_OK)
@modem_to_http_exception
async def set_data_usage_reset_day(modem_id: str, month_day: int) -> DataUsageSettings:
    """
    Set day in month where data usage counter will be reset.
    """
    modem = Modem.get_device(modem_id)

    return modem.set_data_usage_reset_day(month_day)
