from typing import List, Optional

from modem.modem import Modem
from modem.at import ATCommander, ATCommand, ATDivider
from modem.exceptions import ATConnectionError
from modem.models import ModemCellInfo, ModemSignalQuality, PDPInfo, ServingCellInfo, NeighborCellInfo


class LTEEG25G(Modem):
    def _detected(self) -> bool:
        """
        Any port with manufacturer "Quectel" and product "EG25-G" is considered detected for this implementation.
        """
        return any(port.manufacturer == "Quectel" and port.product == "EG25-G" for port in self.ports)

    def _int_or_none(self, value: str) -> Optional[int]:
        try:
            return int(value)
        except Exception:
            return None

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
                PDPInfo(
                    profile_id=info[0],
                    protocol=info[1],
                    apn=info[2],
                    ip_address=info[3],
                    primary_dns=info[4],
                    secondary_dns=info[5],
                    ipv6_address=info[6],
                    status=info[7]
                )
                for info in response.data
            ]

    def set_apn(self, profile: int, apn: str) -> None:
        with self.at_commander() as cmd:
            # Expected: OK
            cmd.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'{profile},"IP","{apn}"', cmd_id_response=False)

    def get_signal_strength(self) -> ModemSignalQuality:
        with self.at_commander() as cmd:
            response = cmd.get_signal_strength()

            return ModemSignalQuality(
                signal_strength=int(response.data[0][0]),
                bit_error_rate=int(response.data[0][1])
            )

    def get_cell_info(self) -> ModemCellInfo:
        with self.at_commander() as cmd:
            # +QENG: "servingcell","NOCONN","LTE","FDD",724,04,482440F,228,9410,28,3,3,8824,-88,-13,-57,10,31
            serving_cell = cmd.get_serving_cell().data[0]
            # +QENG: "neighbourcell intra","LTE",9410,228,-15,-88,-55,0,31,7,30,2,50
            # +QENG: "neighbourcell inter","LTE",400,-,-,-,-,-,-,0,2,7
            neighbor_cells = cmd.get_neighboring_cells()

            if len(serving_cell) < 18:
                serving_cell.extend([None] * (18 - len(serving_cell)))
            for cell in neighbor_cells.data:
                if len(cell) < 13:
                    cell.extend([None] * (13 - len(cell)))

            return ModemCellInfo(
                serving_cell=ServingCellInfo(
                    network_status=serving_cell[1],
                    access_technology=serving_cell[2],
                    duplex_mode=serving_cell[3],
                    mobile_country_code=int(serving_cell[4]),
                    mobile_network_code=int(serving_cell[5]),
                    cell_identity=serving_cell[6],
                    physical_cell_id=int(serving_cell[7]),
                    earfcn=int(serving_cell[8]),
                    frequency_band=int(serving_cell[9]),
                    tracking_area_code=int(serving_cell[10]),
                    reference_signal_power=int(serving_cell[11]),
                    timing_advance=self._int_or_none(serving_cell[12]),
                    reference_signal_received_power=self._int_or_none(serving_cell[13]),
                    reference_signal_received_quality=self._int_or_none(serving_cell[14]),
                    snr=self._int_or_none(serving_cell[15]),
                    uplink_bandwidth=self._int_or_none(serving_cell[16]),
                    downlink_bandwidth=self._int_or_none(serving_cell[17]),
                ),
                neighbor_cells=[
                    NeighborCellInfo(
                        cell_type=cell[0],
                        access_technology=cell[1],
                        earfcn=int(cell[2]),
                        physical_cell_id=self._int_or_none(cell[3]),
                        signal_quality=self._int_or_none(cell[4]),
                        reference_signal_received_power=self._int_or_none(cell[5]),
                        snr=self._int_or_none(cell[6]),
                        timing_advance=self._int_or_none(cell[7]),
                        downlink_bandwidth=self._int_or_none(cell[8]),
                        uplink_bandwidth=self._int_or_none(cell[9]),
                        qrxlevmin=self._int_or_none(cell[10]),
                        signal_quality_threshold=self._int_or_none(cell[11]),
                        signal_strength_threshold=self._int_or_none(cell[12])
                    )
                    for cell in neighbor_cells.data
                ]
            )

    def ping(self, host: str) -> int:
        with self.at_commander() as cmd:
            response = cmd.ping(host)

            return int(response.data[0][0])
