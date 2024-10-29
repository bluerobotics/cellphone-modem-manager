from typing import List

from modem.at import ATCommander, ATCommand, ATDivider
from modem.exceptions import ATConnectionError
from modem.models import (
    ModemCellInfo,
    ModemSignalQuality,
    PDPInfo,
    ServingCellInfo,
    NeighborCellInfo,
)
from modem.modem import Modem
from utils import arr_to_model


class LTEEG25G(Modem):
    def _detected(self) -> bool:
        """
        Any port with manufacturer "Quectel" and product "EG25-G" is considered detected for this implementation.
        """
        return any(port.manufacturer == "Quectel" and port.product == "EG25-G" for port in self.ports)

    def at_commander(self) -> ATCommander:
        # Usually the 3 port is the AT port in Quectel modems, so try it first
        ports = self.ports
        if len(ports) > 3:
            ports = [self.ports[2]] + self.ports[:2] + self.ports[3:]

        for port in ports:
            try:
                return ATCommander(port.device)
            except Exception:
                pass

        raise ATConnectionError(f"Unable to detect any AT port for device {self.device}")

    def reboot(self) -> None:
        with self.at_commander() as cmd:
            cmd.reboot_modem()

    def get_usb_mode(self) -> int:
        with self.at_commander() as cmd:
            # Expected: +QCFG: "usbnet",1
            response = cmd.command(ATCommand.QUERY_CONFIGURATION, ATDivider.EQ, '"usbnet"')

            return int(response.data[0][1])

    def set_usb_mode(self, mode: str) -> None:
        with self.at_commander() as cmd:
            # Expected: OK
            cmd.command(ATCommand.QUERY_CONFIGURATION, ATDivider.EQ, f'"usbnet",{mode}', cmd_id_response=False)

    def get_pdp_info(self) -> List[PDPInfo]:
        with self.at_commander() as cmd:
            response = cmd.get_pdp_info()

            return [
                arr_to_model(info, PDPInfo)
                for info in response.data
            ]

    def set_apn(self, profile: int, apn: str) -> None:
        with self.at_commander() as cmd:
            # Expected: OK
            cmd.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'{profile},"IP","{apn}"', cmd_id_response=False)

    def get_signal_strength(self) -> ModemSignalQuality:
        with self.at_commander() as cmd:
            response = cmd.get_signal_strength()

            return arr_to_model(response.data[0], ModemSignalQuality)

    def get_cell_info(self) -> ModemCellInfo:
        with self.at_commander() as cmd:
            # +QENG: "servingcell","NOCONN","LTE","FDD",724,04,482440F,228,9410,28,3,3,8824,-88,-13,-57,10,31
            serving_cell = cmd.get_serving_cell()
            serving_cell.data[0].pop(0) # Remove the first element since we don't need it
            # +QENG: "neighbourcell intra","LTE",9410,228,-15,-88,-55,0,31,7,30,2,50
            # ...
            # +QENG: "neighbourcell inter","LTE",400,-,-,-,-,-,-,0,2,7
            neighbor_cells = cmd.get_neighboring_cells()

            return ModemCellInfo(
                serving_cell=arr_to_model(serving_cell.data[0], ServingCellInfo),
                neighbor_cells=[
                    arr_to_model(cell, NeighborCellInfo)
                    for cell in neighbor_cells.data
                ]
            )

    def ping(self, host: str) -> int:
        with self.at_commander() as cmd:
            response = cmd.ping(host)

            return int(response.data[0][0])
