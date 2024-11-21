import asyncio
from typing import Optional

from commonwealth.utils.Singleton import Singleton
from loguru import logger


class ModemManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.stop_event = asyncio.Event()

        self.modem_configure_task: Optional[asyncio.Task] = None
        self.modem_usage_task: Optional[asyncio.Task] = None

    async def _wait_for_or_stop(self, delay: int) -> None:
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            pass

    async def configure_modem(self) -> None:
        pass

    async def get_usage_metrics(self) -> None:
        pass

    async def start_modem_configure_task(self) -> None:
        while not self.stop_event.is_set():
            await self.configure_modem()
            await self._wait_for_or_stop(30)

    async def start_modem_usage_task(self) -> None:
        while not self.stop_event.is_set():
            await self.get_usage_metrics()
            await self._wait_for_or_stop(120)

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self.modem_configure_task = loop.create_task(self.start_modem_configure_task())
        self.modem_usage_task = loop.create_task(self.start_modem_usage_task())

    async def stop(self) -> None:
        self.stop_event.set()
        if self.modem_configure_task:
            logger.info("Waiting for the ModemManager.modem_configure_task to finish.")
            await self.modem_configure_task
        if self.modem_usage_task:
            logger.info("Waiting for the ModemManager.modem_usage_task to finish.")
            await self.modem_usage_task
