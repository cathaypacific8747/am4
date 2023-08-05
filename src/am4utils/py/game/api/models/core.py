from typing import Optional
from pydantic import BaseModel, Field
from pydantic import field_validator

class Status(BaseModel):
    success: bool = Field(alias="request", default=False)
    requests_remaining: Optional[int] = None
    description: Optional[str] = None

    @field_validator("success", mode='before')
    @classmethod
    def request_to_bool(cls, v):
        if isinstance(v, str):
            return v == "success"
        return v