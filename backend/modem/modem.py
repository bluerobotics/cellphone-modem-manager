import abc
from typing import List, Type, Optional
from serial.tools.list_ports_linux import SysFS

from utils import get_modem_descriptors
from modem.at import ATCommander
from modem.exceptions import InvalidModemDevice


class Modem(abc.ABC):
    @staticmethod
    def connected_devices() -> List["Modem"]:
        descriptors = get_modem_descriptors()
        return [
            modem for subclass in Modem.__subclasses__()
            for device, ports in descriptors.items()
            if (modem := subclass(device, ports))._detected()
        ]

    @classmethod
    def get_device(cls, device: str) -> Type["Modem"]:
        modem = next((modem for modem in cls.connected_devices() if modem.device == device), None)
        if not modem:
            raise InvalidModemDevice(f"Device {device} not found in any implementation.")

        return modem

    def __init__(self, device: str, ports: List[SysFS]) -> None:
        self.device: str = device
        self.ports: List[SysFS] = ports

        self.manufacturer: Optional[str] = ports[0].manufacturer if len(ports) > 0 else None
        self.product: Optional[str] = ports[0].product if len(ports) > 0 else None

    @abc.abstractmethod
    def _detected(self) -> bool:
        return False

    @abc.abstractmethod
    def at_commander(self) -> ATCommander:
        raise NotImplementedError

    @abc.abstractmethod
    def get_usb_mode(self, number: str):
        raise NotImplementedError

    @abc.abstractmethod
    def set_usb_mode(self, number: str, mode: str):
        raise NotImplementedError
