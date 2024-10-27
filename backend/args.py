import argparse
from dataclasses import dataclass


@dataclass
class CommandLineArgs:
    debug: bool
    host: str
    port: int

    @staticmethod
    def from_args() -> "CommandLineArgs":
        parser = argparse.ArgumentParser(description="Modem Manager extension client.")

        parser.add_argument("--debug", action="store_true", default=False, help="Enable debug mode")
        parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to server Modem Manager extension on")
        parser.add_argument("--port", type=int, default=20038, help="Port to server Modem Manager extension on")

        args = parser.parse_args()
        client_args = CommandLineArgs(debug=args.debug, host=args.host, port=args.port)

        return client_args
