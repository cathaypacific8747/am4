import httpx
import json
import os
from .models.alliance import AllianceResponse
from .models.user import UserResponse
from .models.core import Status
from am4utils.game import AllianceCache
from typing import Tuple

TOKEN = None

async def fetch_alliance(alliance_name: str) -> Tuple[Status, AllianceCache | None]:
    # async with httpx.AsyncClient() as client:
    #     r = await client.get(f'https://www.airlinemanager.com/api/?access_token={TOKEN}&search={alliance_name}')
    #     return AllianceResponse.model_validate_json(r.text)
    
    # TODO: construct a fatal error when pydantic fails to validate the json
    #       also handle network errors
    with open(f'{__path__[0]}/data/A_Valiant Air_1691065293.json') as f:
        ar = AllianceResponse.model_validate_json(f.read())
        if ar.status.request != "success":
            return ar.status, None
    al = ar.alliance[0]
    return ar.status, AllianceCache.create(
        id=al.id,
        name=al.name,
        rank=al.rank,
        member_count=al.member_count,
        max_members=al.max_members,
        value=al.value,
        ipo=al.ipo,
        min_sv=al.min_sv
    )

async def fetch_user(user_query: str | int):
    # async with httpx.AsyncClient() as client:
    #     r = await client.get(f'https://www.airlinemanager.com/api/?access_token={TOKEN}&search={alliance_name}')
    #     return UserResponse.model_validate_json(r.text)
    with open(f'{__path__[0]}/data/U_Maxy Air_1680180000.json') as f:
        alliance = UserResponse.model_validate_json(f.read())
        return alliance
    # TO BE IMPLEMENTED