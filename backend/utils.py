from typing import Dict, List, Any, Type

from pydantic import BaseModel
from serial.tools.list_ports_linux import SysFS, comports


def get_modem_descriptors() -> Dict[str, List[SysFS]]:
    """
    Returns a dictionary with device paths as keys and lists of associated port information as values.
    """
    modem_ports: Dict[str, List[SysFS]] = {}
    for port in sorted(comports(), key=lambda port: port.name):
        # Group ports by their usb_device_path
        if port.usb_device_path is not None:
            modem_ports.setdefault(port.usb_device_path, []).append(port)

    return modem_ports


def arr_to_model(array: List[Any], model: Type) -> List[Any]:
    """
    Converts an array to a pydantic model by adding None values to the end of the array.
    """
    if not issubclass(model, BaseModel):
        raise ValueError("Model must be a subclass of pydantic.BaseModel to be expanded")

    data = array + [None] * (len(model.model_fields) - len(array))

    return model(**dict(zip(list(model.model_fields), data)))
