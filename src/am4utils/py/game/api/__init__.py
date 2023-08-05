import httpx
from .models.alliance import AllianceResponse
from .models.user import UserResponse
from .models.core import Status
from am4utils.game import AllianceLog
from typing import Tuple
from pydantic import ValidationError

TOKEN = None
ENDPOINT = "https://www.airlinemanager.com/api/"

async def fetch_alliance(alliance_name: str, local_file = str | None) -> Tuple[Status, AllianceLog | None]:
    ar: AllianceResponse
    if local_file is None:
        raise NotImplementedError("api querying isn't implemented yet")
        # TODO: create a new network_failure status if request fails
        async with httpx.AsyncClient() as client:
            r = await client.get(f'{ENDPOINT}?access_token={TOKEN}&search={alliance_name}')
            ar = AllianceResponse.model_validate_json(r.text)
    
    # TODO: construct a fatal error when pydantic fails to validate the json
    with open(local_file) as f:
        try:
            ar = AllianceResponse.model_validate_json(f.read())
            if not ar.status.success:
                return ar.status, None
        except ValidationError as exc:
            status = Status()
            status.description = str(exc)
            return status, None

    al = ar.alliance[0]
    return ar.status, AllianceLog(
        id=al.id,
        name=al.name,
        rank=al.rank,
        member_count=al.member_count,
        max_members=al.max_members,
        value=al.value,
        ipo=al.ipo,
        min_sv=al.min_sv,
        members=[AllianceLog.Member(
            id=m.id,
            username=m.username,
            joined=m.joined,
            flights=m.flights,
            contributed=m.contributed,
            daily_contribution=m.daily_contribution,
            online=m.online,
            sv=m.sv,
            season=m.season
        ) for m in ar.members]
    ).insert_to_db()

async def fetch_user(user_query: str | int):
    raise NotImplementedError("TODO")
    # async with httpx.AsyncClient() as client:
    #     r = await client.get(f'https://www.airlinemanager.com/api/?access_token={TOKEN}&search={alliance_name}')
    #     return UserResponse.model_validate_json(r.text)
    with open(f'{__path__[0]}/data/U_Maxy Air_1680180000.json') as f:
        alliance = UserResponse.model_validate_json(f.read())
        return alliance