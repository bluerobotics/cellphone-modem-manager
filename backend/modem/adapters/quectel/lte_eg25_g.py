import time
from functools import wraps
from typing import Any, Callable, List, cast

from modem.at import ATCommand, ATCommander, ATDivider
from modem.exceptions import ATConnectionError, ATConnectionTimeout
from modem.models import (
    AccessTechnology,
    ModemCellInfo,
    ModemSignalQuality,
    NeighborCellType,
    PDPContext,
    USBNetMode,
)
from modem.modem import Modem
from modem.adapters.quectel.at import QuectelATCommand
from modem.adapters.quectel.models import BaseServingCell, BaseNeighborCell
from utils import arr_to_model


class LTEEG25G(Modem):
    """
    Implement configuration and control of Quectel EG25-G modems.
    """

    def _detected(self) -> bool:
        """
        Any port with manufacturer "Quectel" and product "EG25-G" is considered detected for this implementation.
        """
        return any(port.manufacturer == "Quectel" and port.product == "EG25-G" for port in self.ports)

    def at_commander(self, timeout: int = 10) -> ATCommander:
        # Usually the third port is the AT port in Quectel modems, so try it first
        ports = [self.ports[2]] + self.ports[:2] + self.ports[3:] if len(self.ports) > 3 else self.ports

        end_time = time.monotonic() + timeout
        for port in ports:
            while time.monotonic() < end_time:
                if not ATCommander.is_locked(port.device):
                    try:
                        return ATCommander(port.device)
                    except Exception:
                        break
                time.sleep(0.1)

        if time.monotonic() < end_time:
            raise ATConnectionError(f"Unable to detect any AT port for device {self.device}")
        raise ATConnectionTimeout(f"Timeout reached trying to connect to device {self.device}")

    @staticmethod
    def with_at_commander(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: "LTEEG25G", *args: Any, **kwargs: Any) -> Any:
            with self.at_commander() as cmd:
                return func(self, cmd, *args, **kwargs)
        return wrapper  # type: ignore

    @with_at_commander
    def reboot(self, cmd: ATCommander) -> None:
        cmd.reboot_modem()

    @with_at_commander
    def get_usb_net_mode(self, cmd: ATCommander) -> USBNetMode:
        # Expected: +QCFG: "usbnet",1
        response = cmd.command(QuectelATCommand.CONFIGURATION, ATDivider.EQ, '"usbnet"')

        return USBNetMode(response.data[0][1])

    @with_at_commander
    def set_usb_net_mode(self, cmd: ATCommander, mode: USBNetMode) -> None:
        # Expected: OK
        cmd.command(QuectelATCommand.CONFIGURATION, ATDivider.EQ, f'"usbnet",{mode.value}', cmd_id_response=False)

    @with_at_commander
    def get_pdp_info(self, cmd: ATCommander) -> List[PDPContext]:
        response = cmd.get_pdp_info()

        return [
            arr_to_model(info, PDPContext)
            for info in response.data
        ]

    @with_at_commander
    def get_signal_strength(self, cmd: ATCommander) -> ModemSignalQuality:
        response = cmd.get_signal_strength()

        return arr_to_model(response.data[0], ModemSignalQuality)

    @with_at_commander
    def get_cell_info(self, cmd: ATCommander) -> ModemCellInfo:
        serving_cell_data = cmd.command(QuectelATCommand.ENGINEER_MODE, ATDivider.EQ, '"servingcell"').data[0]
        serving_cell_data.pop(0)  # Discard the first element, which is always 'servingcell'

        serving_rat = AccessTechnology(serving_cell_data[1])
        serving_model = BaseServingCell.get_model(serving_rat)
        if not serving_model:
            raise NotImplementedError(f"Cell information for {serving_rat} is not implemented")
        serving_cell = cast(BaseServingCell, arr_to_model(serving_cell_data, serving_model))

        neighbor_cells_data = cmd.command(QuectelATCommand.ENGINEER_MODE, ATDivider.EQ, '"neighbourcell"').data
        neighbor_cells = []
        for neighbor_data in neighbor_cells_data:
            neighbor_type = NeighborCellType(neighbor_data[0])
            neighbor_rat = AccessTechnology(neighbor_data[1])
            neighbor_model = BaseNeighborCell.get_model(serving_rat, neighbor_rat, neighbor_type)
            if neighbor_model:
                neighbor_cell = cast(BaseNeighborCell, arr_to_model(neighbor_data, neighbor_model))
                neighbor_cells.append(neighbor_cell.info())

        return ModemCellInfo(
            serving_cell=serving_cell.info(),
            neighbor_cells=neighbor_cells
        )

    @with_at_commander
    def set_apn(self, cmd: ATCommander, profile: int, apn: str) -> None:
        # Expected: OK
        cmd.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'{profile},"IP","{apn}"', cmd_id_response=False)

    @with_at_commander
    def ping(self, cmd: ATCommander, host: str) -> int:
        response = cmd.command(QuectelATCommand.PING, ATDivider.EQ, f'1,"{host}",1,1')

        return int(response.data[0][0])
