from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from .core import Status

class User(BaseModel):
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
    game_mode: Literal["Easy", "Realism"]
    rank: int
    reputation: int
    cargo_reputation: int 
    founded: datetime
    logo: str

class Share(BaseModel):
    date: datetime
    share: float
    
class Award(BaseModel):
    award: str
    awarded: datetime

class Aircraft(BaseModel):
    aircraft: str
    amount: int
    
class Route(BaseModel):
    dep: str 
    stop: Optional[str] = None
    arrival: str
    distance: int
    arrived: datetime

class UserResponse(BaseModel):
    status: Status 
    user: User
    share_development: List[Share]
    awards: List[Award]
    fleet: List[Aircraft]
    routes: List[Route]