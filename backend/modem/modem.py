import abc
import hashlib
import re
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Type, Self, cast

from commonwealth.settings.manager import PydanticManager
from config import SERVICE_NAME
from settings import SettingsV1, DataUsageSettings, ModemsSettings
from serial.tools.list_ports_linux import SysFS

from modem.at import ATCommander, ATDivider, ATCommand
from modem.exceptions import InvalidModemDevice
from modem.models import (
    ModemDeviceDetails,
    ModemCellInfo,
    ModemClockDetails,
    ModemSignalQuality,
    ModemSIMStatus,
    OperatorInfo,
    PDPContext,
    USBNetMode,
)
from utils import arr_to_model, get_modem_descriptors


class Modem(abc.ABC):
    _manager: PydanticManager = PydanticManager(SERVICE_NAME, SettingsV1)

    @property
    def _settings(self) -> SettingsV1:
        return cast(SettingsV1, self._manager.settings)

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

    def _fetch_modem_settings(self, imei: str) -> ModemsSettings:
        modem: Optional[ModemsSettings] = self._settings.modems.get(imei, None)

        if not modem:
            modem = ModemsSettings(
                identifier=imei,
                configured=False,
                data_usage=DataUsageSettings(),
            )

        return modem

    def _save_modem_settings(self, modem: ModemsSettings) -> None:
        self._settings.modems[modem.identifier] = modem
        self._manager.save()

    # Common AT commands, we supply a basic implementation for all modems but can be overridden if needed by device

    @with_at_commander
    def set_data_usage_alert(self, cmd: ATCommander, total_bytes: int) -> DataUsageSettings:
        modem = self._fetch_modem_settings(cmd.get_imei().data[0][0])
        modem.data_usage.data_limit = total_bytes
        self._save_modem_settings(modem)
        return cast(DataUsageSettings, modem.data_usage)

    @with_at_commander
    def set_data_usage_reset_day(self, cmd: ATCommander, month_day: int) -> DataUsageSettings:
        modem = self._fetch_modem_settings(cmd.get_imei().data[0][0])
        modem.data_usage.data_reset_day = month_day
        self._save_modem_settings(modem)
        return cast(DataUsageSettings, modem.data_usage)

    @with_at_commander
    def get_data_usage_details(self, cmd: ATCommander) -> DataUsageSettings:
        modem = self._fetch_modem_settings(cmd.get_imei().data[0][0])
        return cast(DataUsageSettings, modem.data_usage)

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
    def get_sim_status(self) -> ModemSIMStatus:
        raise NotImplementedError

    @abc.abstractmethod
    def set_auto_data_usage_save(self, interval: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reset_data_usage(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_data_usage(self) -> Tuple[int, int]:
        raise NotImplementedError

    @abc.abstractmethod
    def ping(self, host: str) -> int:
        raise NotImplementedError
