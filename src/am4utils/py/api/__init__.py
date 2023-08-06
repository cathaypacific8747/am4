import httpx
from .models.alliance import AllianceResponse
from .models.user import UserResponse
from .models.core import Status
from am4utils.log import AllianceLog, UserLog
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

async def fetch_user(query: str | int, local_file: str | None) -> Tuple[Status, UserLog | None]:
    ur: UserResponse
    if local_file is None:
        raise NotImplementedError("api querying isn't implemented yet")
        # TODO: create a new network_failure status if request fails
        async with httpx.AsyncClient() as client:
            param = "id" if isinstance(query, int) else "user"
            r = await client.get(f'{ENDPOINT}?access_token={TOKEN}&{param}={query}')
            ur = UserResponse.model_validate_json(r.text)
    
    with open(local_file) as f:
        try:
            ur = UserResponse.model_validate_json(f.read())
            if not ur.status.success:
                return ur.status, None
        except ValidationError as exc:
            status = Status()
            status.description = str(exc)
            return status, None
    
    u = ur.user
    return ur.status, UserLog(
        id=u.id, username=u.username, level=u.level, online=u.online,
        share=u.share, shares_available=u.shares_available, shares_sold=u.shares_sold, ipo=u.ipo,
        fleet_count=u.fleet_count, routes=u.routes, alliance=u.alliance,
        achievements=u.achievements, game_mode=u.game_mode, rank=u.rank, reputation=u.reputation, cargo_reputation=u.cargo_reputation,
        founded=u.founded, logo=u.logo,
        share_log=[UserLog.Share(
            ts=sl.ts,
            share=sl.share
        ) for sl in ur.share_log],
        awards=[UserLog.Award(
            ts=a.ts,
            award=a.award
        ) for a in ur.awards],
        fleet=[],
        route_list=[]
    )