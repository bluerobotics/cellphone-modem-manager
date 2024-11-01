from fastapi import APIRouter, status
from fastapi_versioning import versioned_api_route

from modem import Modem
from modem.models import (
    ModemDevice,
    ModemSignalQuality,
    ModemCellInfo,
    PDPContext,
    USBNetMode
)

modem_router_v1 = APIRouter(
    prefix="/modem",
    tags=["modem_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@modem_router_v1.get("/", status_code=status.HTTP_200_OK)
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
async def fetch_by_id(modem_id: str) -> ModemDevice:
    """
    Get details of a modem by id.
    """
    modem = Modem.get_device(modem_id)

    return ModemDevice(
        device=modem.device,
        id=modem.id,
        manufacturer=modem.manufacturer,
        product=modem.product
    )


@modem_router_v1.get("/{modem_id}/signal", status_code=status.HTTP_200_OK)
async def fetch_signal_strength(modem_id: str) -> ModemSignalQuality:
    """
    Get signal strength of a modem by device id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_signal_strength()


@modem_router_v1.get("/{modem_id}/cell", status_code=status.HTTP_200_OK)
async def fetch_serving_cell_info(modem_id: str) -> ModemCellInfo:
    """
    Get serving cell and neighbors cells information of a modem by device id.
    """
    modem = Modem.get_device(modem_id)

    return modem.get_cell_info()


@modem_router_v1.post("/{modem_id}/reboot", status_code=status.HTTP_204_NO_CONTENT)
async def reboot_by_id(modem_id: str) -> None:
    """
    Reboot a modem by device id.
    """
    modem = Modem.get_device(modem_id)

    return modem.reboot()


@modem_router_v1.get("/{id}/config/usb_net", status_code=status.HTTP_200_OK)
async def fetch_usb_mode(id: str) -> USBNetMode:
    """
    Get USB mode of a modem by device.
    """
    modem = Modem.get_device(id)

    return modem.get_usb_net_mode()


@modem_router_v1.put("/{id}/config/usb_net/{mode}", status_code=status.HTTP_204_NO_CONTENT)
async def set_usb_mode(id: str, mode: USBNetMode) -> None:
    """
    Set USB mode of a modem by device.
    """
    modem = Modem.get_device(id)

    return modem.set_usb_net_mode(mode)


@modem_router_v1.get("/{id}/pdp", status_code=status.HTTP_200_OK)
async def fetch_pdp_info(id: str) -> list[PDPContext]:
    """
    Get PDP information of a modem by device.
    """
    modem = Modem.get_device(id)

    return modem.get_pdp_info()


@modem_router_v1.put("/{id}/pdp/{profile}apn/{apn}", status_code=status.HTTP_204_NO_CONTENT)
async def set_apn_by_profile(id: str, profile: int, apn: str) -> None:
    """
    Set APN of a profile of a modem by device.
    """
    modem = Modem.get_device(id)

    return modem.set_apn(profile, apn)
