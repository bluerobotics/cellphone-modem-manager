from pydantic import BaseModel

class NearbyCellRadio(BaseModel):
    type: str

class NearbyCellTower(BaseModel):
    latitude: float
    longitude: float
    range: int
    radio: NearbyCellRadio
