from pydantic import BaseModel

class PaxTicketDict(BaseModel):
    y: int
    j: int
    f: int

class CargoTicketDict(BaseModel):
    l: float
    h: float

class VIPTicketDict(BaseModel):
    y: int
    j: int
    f: int