from fastapi import APIRouter, status
from fastapi_versioning import versioned_api_route

from modem import Modem
from modem.models import ModemDevice

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
            manufacturer=modem.manufacturer,
            product=modem.product
        )
        for modem in modems
    ]


@modem_router_v1.get("/{device}", status_code=status.HTTP_200_OK)
async def fetch_by_device(device: str) -> ModemDevice:
    """
    Get details of a modem by device.
    """
    modem = Modem.get_device(device)

    return ModemDevice(
        device=modem.device,
        manufacturer=modem.manufacturer,
        product=modem.product
    )
