#! /usr/bin/env python3
import asyncio
import logging

from loguru import logger
from uvicorn import Config, Server

from args import CommandLineArgs
from config import SERVICE_NAME

from api import application


if __name__ == "__main__":
    args = CommandLineArgs.from_args()

    if args.debug:
        logging.getLogger(SERVICE_NAME).setLevel(logging.DEBUG)

    logger.info("Releasing the extension Cellphone Modem Manager.")
    loop = asyncio.new_event_loop()

    config = Config(app=application, loop=loop, host=args.host, port=args.port, log_config=None)
    server = Server(config)

    loop.run_until_complete(server.serve())
