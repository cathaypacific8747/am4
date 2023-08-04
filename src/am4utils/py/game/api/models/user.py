from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
from .core import Status

class User(BaseModel):
    company: str
    level: int 
    online: bool
    share: float
    shares_available: int
    shares_sold: int
    ipo: int
    fleet: int
    routes: int
    alliance: str
    achievements: int
    game_mode: Literal["Easy", "Realism"]
    rank: int
    reputation: int
    cargo_reputation: int 
    founded: datetime
    logo: str

class ShareDevelopment(BaseModel):
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
    share_development: List[ShareDevelopment]
    awards: List[Award]
    fleet: List[Aircraft]
    routes: List[Route]