from modem.adapters.quectel.base import QuectelLTEBase


class LTEEG25G(QuectelLTEBase):
    """
    Implement configuration and control of Quectel EG25-G modems.
    """

    def _detected(self) -> bool:
        """
        Any port with manufacturer "Quectel" and product "EG25-G" is considered detected for this implementation.
        """
        return any("Quectel" in port.manufacturer and "EG25-G" in port.product for port in self.ports)
