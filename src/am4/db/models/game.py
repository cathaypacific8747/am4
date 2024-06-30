from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

from am4.utils.game import User

from .util import assert_equal_property_names

StrToUpper = BeforeValidator(func=lambda x: x.upper().strip() if isinstance(x, str) else x)
StrPctToFloat = BeforeValidator(
    func=lambda x: float(x.replace("%", "e-2")) if isinstance(x, str) and x.endswith("%") else x
)


class PyUser(BaseModel):
    id: str
    username: str
    game_id: Annotated[int, Field(gt=0)]
    game_name: str
    game_mode: Annotated[Literal["EASY", "REALISM"], StrToUpper]
    discord_id: Annotated[int, Field(ge=0)]
    wear_training: Annotated[int, Field(ge=0, le=5)]
    repair_training: Annotated[int, Field(ge=0, le=5)]
    l_training: Annotated[int, Field(ge=0, le=6)]
    h_training: Annotated[int, Field(ge=0, le=6)]
    fuel_training: Annotated[int, Field(ge=0, le=3)]
    co2_training: Annotated[int, Field(ge=0, le=5)]
    fuel_price: Annotated[int, Field(ge=0, le=3000)]
    co2_price: Annotated[int, Field(ge=0, le=200)]
    accumulated_count: Annotated[int, Field(ge=0)]
    load: Annotated[float, Field(ge=0, le=1), StrPctToFloat]
    income_loss_tol: Annotated[float, Field(ge=0, le=1), StrPctToFloat]
    fourx: bool
    role: Annotated[
        Literal[
            "BANNED",
            "USER",
            "TRUSTED_USER",
            "HIGHLY_TRUSTED_USER",
            "TOP_ALLIANCE_MEMBER",
            "TOP_ALLIANCE_ADMIN",
            "HELPER",
            "MODERATOR",
            "ADMIN",
            "SUPERUSER",
        ],
        StrToUpper,
    ]
    valid: bool


PyUserWhitelistedKeys = Literal[
    "game_id",
    "game_name",
    "game_mode",
    "wear_training",
    "repair_training",
    "l_training",
    "h_training",
    "fuel_training",
    "co2_training",
    "fuel_price",
    "co2_price",
    "accumulated_count",
    "load",
    "income_loss_tol",
    "fourx",
]

assert_equal_property_names(User, PyUser)
