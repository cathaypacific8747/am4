from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .core import Status

class User(BaseModel):
    id: Optional[int] = 0
    username: str = Field(alias="company")
    level: int 
    online: bool
    share: float
    shares_available: int
    shares_sold: int
    ipo: int
    fleet_count: int = Field(alias="fleet")
    routes: int
    alliance: str
    achievements: int
    game_mode: bool
    rank: int
    reputation: int
    cargo_reputation: int 
    founded: datetime
    logo: str

    @field_validator("game_mode", mode='before')
    @classmethod
    def game_mode_to_bool(cls, v: str | bool):
        return v == "Realism" if isinstance(v, str) else v

class Share(BaseModel):
    ts: datetime = Field(alias="date")
    share: float
    
class Award(BaseModel):
    ts: datetime = Field(alias="awarded")
    award: str

class AircraftCount(BaseModel):
    aircraft: str
    amount: int
    
class RouteDetail(BaseModel):
    origin: str = Field(alias="dep")
    stopover: str = Field(alias="stop", default='')
    destination: str = Field(alias="arrival")
    distance: int
    arrived: datetime

    @field_validator("stopover", mode='before')
    @classmethod
    def stopover_null_to_empty(cls, v: str | None):
        return '' if v is None else v

class UserResponse(BaseModel):
    status: Status 
    user: User
    share_log: List[Share] = Field(alias="share_development")
    awards: List[Award]
    fleet: List[AircraftCount]
    route_list: List[RouteDetail] = Field(alias="routes")