import abc
import hashlib
import re
from functools import wraps
from typing import Any, Callable, List, Optional, Type, Self, cast

from serial.tools.list_ports_linux import SysFS

from modem.at import ATCommander, ATDivider, ATCommand
from modem.exceptions import InvalidModemDevice
from modem.models import (
    ModemDeviceDetails,
    ModemCellInfo,
    ModemClockDetails,
    ModemFirmwareRevision,
    ModemSignalQuality,
    OperatorInfo,
    PDPContext,
    USBNetMode,
)
from utils import arr_to_model, get_modem_descriptors


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
    def get_device(cls, id: str) -> Type["Modem"]:
        modem = next((modem for modem in cls.connected_devices() if modem.id == id), None)
        if not modem:
            raise InvalidModemDevice(f"Device {id} not found in any implementation.")

        return modem

    def __init__(self, device: str, ports: List[SysFS]) -> None:
        self.device: str = device
        # We create a simple hash to be easy to frontend to identify the modem
        self.id = hashlib.md5(self.device.encode()).hexdigest()
        self.ports: List[SysFS] = ports

        self.manufacturer: Optional[str] = ports[0].manufacturer if len(ports) > 0 else None
        self.product: Optional[str] = ports[0].product if len(ports) > 0 else None

    @abc.abstractmethod
    def _detected(self) -> bool:
        return False

    @abc.abstractmethod
    def at_commander(self) -> ATCommander:
        raise NotImplementedError

    @staticmethod
    def with_at_commander(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: Self, *args: Any, **kwargs: Any) -> Any:
            with self.at_commander() as cmd:
                return func(self, cmd, *args, **kwargs)
        return wrapper  # type: ignore

    # Common AT commands, we supply a basic implementation for all modems but can be overridden if needed by device

    @with_at_commander
    def reboot(self, cmd: ATCommander) -> None:
        cmd.reboot_modem()

    @with_at_commander
    def factory_reset(self, cmd: ATCommander) -> None:
        cmd.reset_to_factory()

    @with_at_commander
    def get_pdp_info(self, cmd: ATCommander) -> List[PDPContext]:
        response = cmd.get_pdp_info()

        return [
            arr_to_model(info, PDPContext)
            for info in response.data
        ]

    @with_at_commander
    def get_operator_info(self, cmd: ATCommander) -> OperatorInfo:
        return arr_to_model(cmd.get_operator_info().data[0], OperatorInfo)

    @with_at_commander
    def get_signal_strength(self, cmd: ATCommander) -> ModemSignalQuality:
        data = cast(
            ModemSignalQuality,
            arr_to_model(cmd.get_signal_strength().data[0], ModemSignalQuality)
        )

        data.signal_strength_dbm = 2 * data.signal_strength_dbm - 113

        return data

    @with_at_commander
    def set_apn(self, cmd: ATCommander, profile: int, apn: str) -> None:
        cmd.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'{profile},"IP","{apn}"', cmd_id_response=False)

    @with_at_commander
    def get_clock(self, cmd: ATCommander) -> ModemClockDetails:
        response = cmd.get_clock().data[0]
        time_str = re.match(r"(\d{2}:\d{2}:\d{2})([-+]\d{2})", response[1])

        return ModemClockDetails(
            date=response[0],
            time=time_str.group(1),
            gmt_offset=int(time_str.group(2)),
        )

    # Abstract and must be implemented by device class

    @abc.abstractmethod
    def get_mt_info(self) -> ModemDeviceDetails:
        raise NotImplementedError

    @abc.abstractmethod
    def get_usb_net_mode(self) -> USBNetMode:
        raise NotImplementedError

    @abc.abstractmethod
    def set_usb_net_mode(self, mode: USBNetMode) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_cell_info(self) -> ModemCellInfo:
        raise NotImplementedError

    @abc.abstractmethod
    def ping(self, host: str) -> int:
        raise NotImplementedError
