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


def arr_to_model(array: List[Any], model: Type) -> Any:
    """
    Converts an array to a pydantic model by adding None values to the end of the array.
    """
    if not issubclass(model, BaseModel):
        raise ValueError("Model must be a subclass of pydantic.BaseModel to be expanded")

    data = array + [None] * (len(model.model_fields) - len(array))

    return model(**dict(zip(list(model.model_fields), data)))


def string_to_unicode_array(input_string: str, total_length: int) -> List[str]:
    """
    Converts a string to a list of unicode characters with a fixed length.
    """
    if len(input_string) > total_length:
        raise ValueError("Input string length must be less than or equal to the total length")

    unicode_array = [str(char) for char in input_string]
    unicode_array.extend(u"0" * (total_length - len(unicode_array)))
    return unicode_array
