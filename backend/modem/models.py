from pydantic import BaseModel

class ModemDevice(BaseModel):
    device: str
