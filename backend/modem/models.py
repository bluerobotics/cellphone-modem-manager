from pydantic import BaseModel

class ModemDevice(BaseModel):
    device: str
    id: str
    manufacturer: str
    product: str
