import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import serial

from modem.exceptions import ATConnectionError, SerialSafeReadFailed, SerialSafeWriteFailed

class ATCommand(Enum):
    AT = "AT"

    SET_ECHO_MODE = "ATE"
    SET_CMD_LINE_TERM = "ATS3"
    SET_RESP_FORMAT_CHAR = "ATS4"
    SET_CMD_LINE_END_CHAR = "ATS5"

    RESET_TO_FACTORY = "AT&F"

    QUERY_CONFIGURATION = "AT+QCFG"
    CONFIGURE_FUNCTIONALITY = "AT+CFUN"
    CONFIGURE_PDP_CONTEXT = "AT+CGDCONT"
    CHECK_SIGNAL_QUALITY = "AT+CSQ"
    CONFIGURE_OPERATOR = "AT+COPS"
    CONFIGURE_CLOCK = "AT+CCLK"


class ATDivider(Enum):
    UNDEFINED = ""
    EQ = "="
    QUESTION = "?"


@dataclass
class ATResponse:
    status: str
    response: Optional[str] = None


class ATCommander:
    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(self.port, self.baud)
        self.ser.timeout = 1 # Max timeout

        # Clear buffers
        self.ser.flush()
        self.ser.read_all()

        if not self.check_ok():
            raise ATConnectionError("Failed to read 'OK' from serial port")

        self._configure_terminators()

    def _configure_terminators(self) -> None:
        # Set terminators
        self.command(ATCommand.SET_CMD_LINE_TERM, ATDivider.EQ, "13")
        self.command(ATCommand.SET_RESP_FORMAT_CHAR, ATDivider.EQ, "10")

        self.command(ATCommand.SET_CMD_LINE_END_CHAR, ATDivider.EQ, "13")

        # Disable ECHO
        self.command(ATCommand.SET_ECHO_MODE, ATDivider.UNDEFINED, "0")

    def _close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _safe_read(self) -> ATResponse:
        try:
            data = self.ser.read_all()
        except serial.SerialTimeoutException as e:
            raise SerialSafeReadFailed(f"Failed to read all bytes from serial device at {self.port_device}") from e

        decoded_data = data.decode("ascii")

        parts = [
            part
            for part in (decoded_data.split('\r\n') if '\r\n' in decoded_data else decoded_data.split('\r'))
            if part
        ]

        print(parts)

        if len(parts) > 1:
            return ATResponse(parts[1], parts[0])
        return ATResponse(parts[0])

    def _safe_serial_write(self, data: str) -> None:
        bytes_written = self.ser.write(data.encode("ascii"))
        self.ser.flush()
        if bytes_written != len(data):
            raise SerialSafeWriteFailed(f"Failed to write all bytes to serial device at {self.port_device}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def raw_command(self, command: str) -> ATResponse:
        self._safe_serial_write(f"{command}\r\n")
        # Commands usually 300ms to respond
        time.sleep(0.35)
        return self._safe_read()

    def command(self, command: ATCommand, divider: ATDivider = ATDivider.UNDEFINED, data: str = "") -> ATResponse:
        return self.raw_command(f"{command.value}{divider.value}{data}\r\n")

    def check_ok(self) -> bool:
        response = self.command(ATCommand.AT)
        # We need to cover cases where terminators are not set
        return (
            "OK" in response.status or
            "ok" in response.status or
            "OK" in response.response or
            "ok" in response.response
        )

    def set_apn(self, apn: str) -> str:
        return self.command(ATCommand.CONFIGURE_PDP_CONTEXT, ATDivider.EQ, f'1,"IP","{apn}"')

    def get_signal_strength(self) -> str:
        return self.command(ATCommand.CHECK_SIGNAL_QUALITY)

    def get_network_info(self) -> str:
        return self.command(ATCommand.CONFIGURE_OPERATOR, ATDivider.QUESTION)

    def get_clock(self) -> str:
        return self.command(ATCommand.CONFIGURE_CLOCK, ATDivider.QUESTION)

    def reboot_modem(self) -> str:
        return self.command(ATCommand.CONFIGURE_FUNCTIONALITY, ATDivider.EQ, "1,1")

    def reset_to_factory(self) -> str:
        return self.command(ATCommand.RESET_TO_FACTORY)
