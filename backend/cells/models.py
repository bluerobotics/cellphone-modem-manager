from pydantic import BaseModel

# General modem related

class CellLocation(BaseModel):
    latitude: float
    longitude: float
    range: int
