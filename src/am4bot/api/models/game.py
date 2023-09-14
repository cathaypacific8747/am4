from typing import Literal
from pydantic import BaseModel, Field, conint, confloat


class User(BaseModel):
    id: str
    username: str
    game_id: conint(ge=0)
    game_name: str
    game_mode: Literal["EASY", "REALISM"]
    discord_id: conint(ge=0)
    wear_training: conint(ge=0, le=5)
    repair_training: conint(ge=0, le=5)
    l_training: conint(ge=0, le=6)
    h_training: conint(ge=0, le=6)
    fuel_training: conint(ge=0, le=3)
    co2_training: conint(ge=0, le=5)
    fuel_price: conint(ge=0, le=3000)
    co2_price: conint(ge=0, le=200)
    accumulated_count: conint(ge=0)
    load: confloat(ge=0, le=1)
    income_loss_tol: confloat(ge=0, le=1)
    fourx: bool
    role: Literal[
        "USER", "TRUSTED_USER", "TRUSTED_USER_2", "TOP_ALLIANCE_MEMBER",
        "TOP_ALLIANCE_ADMIN", "HELPER", "MODERATOR", "ADMIN", "GLOBAL_ADMIN"
    ]
    valid: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    status: str = Field("success", frozen=True)
    user: User

class UserNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)