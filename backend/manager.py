import asyncio
from datetime import datetime, timedelta
from typing import Optional

from commonwealth.utils.Singleton import Singleton
from loguru import logger

from mavlink import MAVLink2Rest, MAVSeverity
from modem import Modem
from modem.models import USBNetMode


class ModemManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.stop_event = asyncio.Event()

        self.modem_configure_task: Optional[asyncio.Task] = None
        self.modem_usage_task: Optional[asyncio.Task] = None
        self.external_positioning_task: Optional[asyncio.Task] = None

    async def _wait_for_or_stop(self, delay: int) -> None:
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            pass

    async def _configure_modem(self) -> None:
        for connected_modem in Modem.connected_devices():
            try:
                imei = await connected_modem.get_imei()
                modem_settings = connected_modem._fetch_modem_settings(imei)

                if modem_settings.configured:
                    continue
                logger.info(f"Configuring modem with IMEI: {imei} to default settings.")

                # We want clock to be automatically synced and use cdc_ether
                await connected_modem.set_automatic_time_sync(True)
                await connected_modem.set_usb_net_mode(USBNetMode.ECM)
                await connected_modem.set_auto_data_usage_save(60)
                await connected_modem.reboot()

                modem_settings.configured = True
                connected_modem._save_modem_settings(modem_settings)
                logger.info(f"Modem with IMEI: {imei} configured successfully.")
            except Exception as e:
                logger.error(f"Error configuring modem: {e}")

    async def _get_usage_metrics(self) -> None:
        for connected_modem in Modem.connected_devices():
            try:
                imei = await connected_modem.get_imei()
                modem_settings = connected_modem._fetch_modem_settings(imei)

                # Get current date to use as base for other calculations
                current_date = datetime.now()

                # We try to get from settings last reset date, if not available we use min date
                last_reset_date = (
                    datetime.strptime(modem_settings.data_usage.last_reset_date, "%Y-%m-%d")
                    if modem_settings.data_usage.last_reset_date
                    else datetime.min
                )

                # If we pass one month since last reset, we should reset the modem accumulator or if user is running
                # and we are in the reset day
                if (
                    current_date - last_reset_date > timedelta(days=31) or
                    current_date.day == modem_settings.data_usage.data_reset_day
                ):
                    # In case more than one point is stored, we should clear modem accumulator
                    if len(modem_settings.data_usage.data_points) > 1:
                        await connected_modem.reset_data_usage()
                        modem_settings.data_usage.last_reset_date = current_date.strftime("%Y-%m-%d")
                    # As we clear the stored data, and after one point will be added, we will keep it updating but
                    # we will not reset the modem accumulator next call since only one point will be stored
                    modem_settings.data_usage.data_points = {}

                data_usage = await connected_modem.get_data_usage()
                modem_settings.data_usage.data_used = data_usage
                modem_settings.data_usage.data_points[current_date.strftime("%Y-%m-%d")] = data_usage
                connected_modem._save_modem_settings(modem_settings)

                if not modem_settings.data_usage.data_control_enabled:
                    continue

                await MAVLink2Rest.send_named_float("DATA_USED", modem_settings.data_usage.total_data_used())

                if modem_settings.data_usage.total_data_used() > modem_settings.data_usage.data_limit:
                    await MAVLink2Rest.send_status_text(
                        f"Data limit reached for modem: {imei[:15]}", MAVSeverity.ALERT
                    )
            except Exception as e:
                logger.error(f"Error getting usage metrics: {e}")

    async def _get_external_positioning(self) -> None:
        try:
            positions = [
                await MAVLink2Rest.get_global_position(id)
                for id in await MAVLink2Rest.get_valid_vehicle_ids()
            ]
            if not any(positions):
                return

            for position in positions:
                raw_latitude = position.get("lat", 0)
                raw_longitude = position.get("lon", 0)

                if raw_latitude != 0 or raw_longitude != 0:
                    return Modem.set_external_positioning(raw_latitude / 1e7, raw_longitude / 1e7)

            return Modem.clear_external_positioning()
        except Exception as e:
            logger.error(f"Error getting external positioning: {e}")

    async def start_modem_configure_task(self) -> None:
        while not self.stop_event.is_set():
            await self._configure_modem()
            await self._wait_for_or_stop(30)

    async def start_modem_usage_task(self) -> None:
        # Apply a shift between tasks to reduce number of concurrent lock tries
        await asyncio.sleep(15)
        while not self.stop_event.is_set():
            await self._get_usage_metrics()
            await self._wait_for_or_stop(120)

    async def start_external_positioning_task(self) -> None:
        while not self.stop_event.is_set():
            await self._get_external_positioning()
            await self._wait_for_or_stop(60)

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self.modem_configure_task = loop.create_task(self.start_modem_configure_task())
        self.modem_usage_task = loop.create_task(self.start_modem_usage_task())
        self.external_positioning_task = loop.create_task(self.start_external_positioning_task())

    async def stop(self) -> None:
        self.stop_event.set()
        if self.external_positioning_task:
            logger.info("Waiting for the ModemManager.external_positioning_task to finish.")
            await self.external_positioning_task
        if self.modem_configure_task:
            logger.info("Waiting for the ModemManager.modem_configure_task to finish.")
            await self.modem_configure_task
        if self.modem_usage_task:
            logger.info("Waiting for the ModemManager.modem_usage_task to finish.")
            await self.modem_usage_task
