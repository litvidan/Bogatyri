from pydantic import BaseModel

class FrequencyRequest(BaseModel):
    freq: int

class BeaconConfig(BaseModel):
    x: float
    y: float
    name: str

class Message(BaseModel):
    data: dict[str : int]

class PositionResponse(BaseModel):
    x: float
    y: float
    accuracy: float