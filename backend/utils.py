from typing import Dict, List
from serial.tools.list_ports_linux import SysFS, comports


def get_modem_descriptors() -> Dict[str, List[SysFS]]:
    """
    Returns a dictionary with device paths as keys and lists of associated port information as values.
    """
    modem_ports: Dict[str, List[SysFS]] = {}
    for port in sorted(comports(), key=lambda port: port.name):
        # Group ports by their usb_device_path
        modem_ports.setdefault(port.usb_device_path, []).append(port)

    return modem_ports
