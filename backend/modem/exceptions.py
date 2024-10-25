class ATConnectionError(Exception):
    """Raised when the modem fails to establish an AT connection."""

class SerialSafeReadFailed(Exception):
    """Raised when the serial port fails to read the expected number of bytes within the timeout period."""

class SerialSafeWriteFailed(Exception):
    """Raised when the serial port fails to write the expected number of bytes."""

class InvalidModemDevice(Exception):
    """Raised when trying to get a implementation class for a modem device that does not exist."""
