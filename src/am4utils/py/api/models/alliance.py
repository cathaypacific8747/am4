
from typing import List, Optional
from pydantic import BaseModel, Field
from .core import Status
from datetime import datetime

class Alliance(BaseModel):
    id: Optional[int] = 0
    name: str
    rank: int
    member_count: int = Field(alias="members")
    max_members: int = Field(alias="maxMembers")
    value: int # broken!
    ipo: bool
    min_sv: float = Field(alias="minSV")

class Member(BaseModel):
    id: Optional[int] = 0
    username: str = Field(alias="company")
    joined: datetime
    flights: int
    contributed: int
    daily_contribution: int = Field(alias="dailyContribution")
    online: datetime
    sv: float = Field(alias="shareValue")
    season: Optional[int] = 0 # none if alliance not participating in season

class AllianceResponse(BaseModel):
    status: Status
    alliance: List[Alliance]
    members: List[Member]