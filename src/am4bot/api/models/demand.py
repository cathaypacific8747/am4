from pydantic import BaseModel

class PaxDemandDict(BaseModel):
    y: int
    j: int
    f: int

class CargoDemandDict(BaseModel):
    l: int
    h: int