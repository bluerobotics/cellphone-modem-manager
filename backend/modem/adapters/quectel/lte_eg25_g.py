import time
from typing import cast

from modem.adapters.quectel.at import QuectelATCommand
from modem.adapters.quectel.models import BaseServingCell, BaseNeighborCell
from modem.at import ATCommander, ATDivider
from modem.exceptions import ATConnectionError, ATConnectionTimeout
from modem.models import (
    AccessTechnology,
    ModemDeviceDetails,
    ModemFirmwareRevision,
    ModemCellInfo,
    ModemSIMStatus,
    NeighborCellType,
    USBNetMode,
)
from modem.modem import Modem
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

    @Modem.with_at_commander
    def get_mt_info(self, cmd: ATCommander) -> ModemDeviceDetails:
        # Since this modem provides all necessary info in a single command, we can override the default.
        # Expected ATI
        # Quectel
        # EG25
        # Revision: EG25GGBR07A08M2G_BETA0416
        # OK
        # Expected: AT+CVERSION
        # VERSION: EG25GGBR07A08M2G_BETA0416
        # Apr 16 2020 20:32:01
        # Authors: QCT
        # OK
        response = cmd.get_mt_info().data[0]
        firmware = cmd.get_firmware_version_details().data[0]
        imei = cmd.get_imei().data[0]
        serial_number = cmd.get_serial_number().data[0]
        imsi = cmd.get_international_mobile_subscriber_id().data[0]

        return ModemDeviceDetails(
            device=self.device,
            id=self.id,
            manufacturer=response[0],
            product=response[1],
            imei=imei[0],
            imsi=imsi[0],
            serial_number=serial_number[0],
            firmware_revision=ModemFirmwareRevision(
                firmware_revision=firmware[0].replace("VERSION: ", ""),
                timestamp=firmware[1],
                authors=firmware[2],
            )
        )

    @Modem.with_at_commander
    def get_usb_net_mode(self, cmd: ATCommander) -> USBNetMode:
        # Expected: +QCFG: "usbnet",1
        response = cmd.command(QuectelATCommand.CONFIGURATION, ATDivider.EQ, '"usbnet"')

        return USBNetMode(response.data[0][1])

    @Modem.with_at_commander
    def set_usb_net_mode(self, cmd: ATCommander, mode: USBNetMode) -> None:
        # Expected: OK
        cmd.command(QuectelATCommand.CONFIGURATION, ATDivider.EQ, f'"usbnet",{mode.value}', cmd_id_response=False)

    @Modem.with_at_commander
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

    @Modem.with_at_commander
    def get_sim_status(self, cmd: ATCommander) -> ModemSIMStatus:
        response = cmd.command(QuectelATCommand.SIM_STATUS, ATDivider.QUESTION)

        return ModemSIMStatus(response.data[0][1])

    @Modem.with_at_commander
    def ping(self, cmd: ATCommander, host: str) -> int:
        response = cmd.command(QuectelATCommand.PING, ATDivider.EQ, f'1,"{host}",1,1')

        return int(response.data[0][0])
