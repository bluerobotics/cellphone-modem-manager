import time
from enum import Enum

import serial

from modem.exceptions import ATConnectionError, SerialSafeReadFailed, SerialSafeWriteFailed


class ATCommands(Enum):
    AT = "AT"
    AT_QCFG = "AT+QCFG"
    AT_CFUN = "AT+CFUN"
    AT_CGDCONT = "AT+CGDCONT"
    AT_CSQ = "AT+CSQ"
    AT_COPS = "AT+COPS"
    AT_CCLK = "AT+CCLK"


class ATDivider(Enum):
    UNDEFINED = ""
    EQ = "="
    QUESTION = "?"


class ATCommander:
    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(self.port, self.baud)
        self.ser.timeout = 1

        self.ser.flush()
        self.ser.read_all()

        if not self.check_ok():
            raise ATConnectionError("Failed to read 'OK' from serial port")

    def _close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _safe_read(self) -> str:
        try:
            data = self.ser.read_all()
        except serial.SerialTimeoutException as e:
            raise SerialSafeReadFailed(f"Failed to read all bytes from serial device at {self.port_device}") from e
        return data.decode("ascii")

    def _safe_serial_write(self, data: str) -> None:
        bytes_written = self.ser.write(data.encode("ascii"))
        self.ser.flush()
        if bytes_written != len(data):
            raise SerialSafeWriteFailed(f"Failed to write all bytes to serial device at {self.port_device}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def raw_command(self, command: str) -> str:
        self._safe_serial_write(f"{command}\r\n")
        time.sleep(0.2)
        return self._safe_read()

    def command(self, command: ATCommands, divider: ATDivider = ATDivider.UNDEFINED, data: str = "") -> str:
        return self.raw_command(f"{command.value}{divider.value}{data}\r\n")

    def check_ok(self) -> bool:
        """Send 'AT' command to verify communication."""
        response = self.command(ATCommands.AT)
        return "OK" in response or "ok" in response

    def set_apn(self, apn: str) -> str:
        return self.command(ATCommands.AT_CGDCONT, ATDivider.EQ, f'1,"IP","{apn}"')

    def get_signal_strength(self) -> str:
        return self.command(ATCommands.AT_CSQ)

    def get_network_info(self) -> str:
        return self.command(ATCommands.AT_COPS, ATDivider.QUESTION)

    def get_clock(self) -> str:
        return self.command(ATCommands.AT_CCLK, ATDivider.QUESTION)

    def reboot_modem(self) -> str:
        return self.command(ATCommands.AT_CFUN, ATDivider.EQ, "1,1")
