from modem.adapters.quectel.base import QuectelLTEBase


class LTEEC25(QuectelLTEBase):
    """
    Implement configuration and control of Quectel EC25 modems.
    """

    def _detected(self) -> bool:
        """
        Any port with manufacturer "Quectel" and product "EC25" is considered detected for this implementation.
        """
        return any("Quectel" in port.manufacturer and "EC25" in port.product for port in self.ports)
