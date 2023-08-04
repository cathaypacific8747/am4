from typing import Literal, Optional
from pydantic import BaseModel

class Status(BaseModel):
    request: Literal["success", "failed"]
    requests_remaining: Optional[int] = None
    description: Optional[str] = None