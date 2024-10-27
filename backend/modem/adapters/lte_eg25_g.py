from modem.modem import Modem
from modem.at import ATCommander, ATCommand, ATDivider
from modem.exceptions import ATConnectionError


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

    def get_usb_mode(self):
        with self.at_commander() as commander:
            return commander.command(ATCommand.QUERY_CONFIGURATION, ATDivider.EQ, "usbnet")

    def set_usb_mode(self, number: str):
        with self.at_commander() as commander:
            return commander.command(ATCommand.QUERY_CONFIGURATION, ATDivider.EQ, f"usbnet, {number}")
