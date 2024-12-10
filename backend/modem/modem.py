import abc
import hashlib
import re
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Type, Self, cast

from commonwealth.settings.manager import PydanticManager
from config import SERVICE_NAME
from settings import SettingsV1, DataUsageSettings, DataUsageControlSettings, ModemsSettings
from serial.tools.list_ports_linux import SysFS

from modem.at import ATCommander, ATDivider, ATCommand
from modem.exceptions import InvalidModemDevice, InexistentModemPosition
from modem.models import (
    ModemDeviceDetails,
    ModemCellInfo,
    ModemClockDetails,
    ModemPosition,
    ModemSignalQuality,
    ModemSIMStatus,
    ModemFunctionality,
    OperatorInfo,
    PDPContext,
    USBNetMode,
)
from utils import arr_to_model, get_modem_descriptors


class Modem(abc.ABC):
    _manager: PydanticManager = PydanticManager(SERVICE_NAME, SettingsV1)

    # This allow other modules to set a backup position in case the modem does not provide one
    _external_position: Optional[Tuple[float, float]] = None

    @property
    def _settings(self) -> SettingsV1:
        return cast(SettingsV1, self._manager.settings)

    @staticmethod
    def connected_devices() -> List["Modem"]:
        def get_all_subclasses(cls: Type) -> List[Type]:
            subclasses = cls.__subclasses__()
            for subclass in subclasses:
                subclasses.extend(get_all_subclasses(subclass))
            return subclasses

        descriptors = get_modem_descriptors()
        all_modem_classes = get_all_subclasses(Modem)
        return [
            modem
            for subclass in all_modem_classes
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
    async def at_commander(self) -> ATCommander:
        raise NotImplementedError

    @staticmethod
    def with_at_commander(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(self: Self, *args: Any, **kwargs: Any) -> Any:
            cmd = await self.at_commander()
            with cmd:
                return await func(self, cmd, *args, **kwargs)
        return wrapper

    @classmethod
    def set_external_positioning(cls, latitude: float, longitude: float) -> None:
        cls._external_position = (latitude, longitude)

    @classmethod
    def clear_external_positioning(cls) -> None:
        cls._external_position = None

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

    async def set_data_usage_control(self, control: DataUsageControlSettings) -> DataUsageSettings:
        modem = self._fetch_modem_settings(await self.get_imei())
        modem.data_usage.data_control_enabled = control.data_control_enabled
        modem.data_usage.data_limit = control.data_limit
        modem.data_usage.data_reset_day = control.data_reset_day
        self._save_modem_settings(modem)
        return cast(DataUsageSettings, modem.data_usage)

    async def get_data_usage_details(self) -> DataUsageSettings:
        modem = self._fetch_modem_settings(await self.get_imei())
        return cast(DataUsageSettings, modem.data_usage)

    @with_at_commander
    async def reboot(self, cmd: ATCommander) -> None:
        await cmd.reboot_modem()

    @with_at_commander
    async def disable(self, cmd: ATCommander) -> None:
        await cmd.disable_modem()

    @with_at_commander
    async def get_functionality(self, cmd: ATCommander) -> ModemFunctionality:
        response = await cmd.command(ATCommand.CONFIGURE_FUNCTIONALITY, ATDivider.QUESTION)
        return ModemFunctionality(response.data[0][0])

    @with_at_commander
    async def factory_reset(self, cmd: ATCommander) -> None:
        await cmd.reset_to_factory()

    @with_at_commander
    async def get_pdp_info(self, cmd: ATCommander) -> List[PDPContext]:
        response = await cmd.get_pdp_info()

        return [
            arr_to_model(info, PDPContext)
            for info in response.data
        ]

    @with_at_commander
    async def get_operator_info(self, cmd: ATCommander) -> OperatorInfo:
        return arr_to_model((await cmd.get_operator_info()).data[0], OperatorInfo)

    @with_at_commander
    async def get_signal_strength(self, cmd: ATCommander) -> ModemSignalQuality:
        data = cast(
            ModemSignalQuality,
            arr_to_model((await cmd.get_signal_strength()).data[0], ModemSignalQuality)
        )

        data.signal_strength_dbm = 2 * data.signal_strength_dbm - 113

        return data

    @with_at_commander
    async def set_apn(self, cmd: ATCommander, profile: int, apn: str) -> None:
        await cmd.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'{profile},"IP","{apn}"', cmd_id_response=False)

    @with_at_commander
    async def get_clock(self, cmd: ATCommander) -> ModemClockDetails:
        response = (await cmd.get_clock()).data[0]
        time_str = re.match(r"(\d{2}:\d{2}:\d{2})([-+]\d{2})", response[1])

        return ModemClockDetails(
            date=response[0],
            time=time_str.group(1),
            gmt_offset=int(time_str.group(2)) / 4,
        )

    @with_at_commander
    async def get_imei(self, cmd: ATCommander) -> str:
        return (await cmd.get_imei()).data[0][0]

    async def get_position(self) -> Optional[ModemPosition]:
        if not self._external_position:
            raise InexistentModemPosition("Modem does not have internal or external position sources.")

        return ModemPosition(
            latitude=self._external_position[0],
            longitude=self._external_position[1],
            external_source=True
        )

    # Abstract and must be implemented by device class

    @abc.abstractmethod
    async def get_mt_info(self) -> ModemDeviceDetails:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_usb_net_mode(self) -> USBNetMode:
        raise NotImplementedError

    @abc.abstractmethod
    async def set_usb_net_mode(self, mode: USBNetMode) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_cell_info(self) -> ModemCellInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_sim_status(self) -> ModemSIMStatus:
        raise NotImplementedError

    @abc.abstractmethod
    async def set_auto_data_usage_save(self, interval: int = 60) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def reset_data_usage(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_data_usage(self) -> Tuple[int, int]:
        raise NotImplementedError

    @abc.abstractmethod
    async def set_automatic_time_sync(self, enabled: bool = True) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def ping(self, host: str) -> int:
        raise NotImplementedError
