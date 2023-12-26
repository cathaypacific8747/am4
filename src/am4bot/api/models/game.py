from typing import Literal

from am4utils.game import User
from pydantic import BaseModel, Field, confloat, conint

from .util import assert_equal_property_names


class PyUser(BaseModel):
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
        "USER", "TRUSTED_USER", "HIGHLY_TRUSTED_USER", "TOP_ALLIANCE_MEMBER",
        "TOP_ALLIANCE_ADMIN", "HELPER", "MODERATOR", "ADMIN", "SUPERUSER"
    ]
    valid: bool

assert_equal_property_names(User, PyUser)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    status: str = Field("success", frozen=True)
    user: PyUser

class UserNotFoundResponse(BaseModel):
    status: str = Field("not_found", frozen=True)
