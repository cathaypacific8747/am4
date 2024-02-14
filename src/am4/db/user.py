from datetime import datetime
from typing import Literal

from am4.utils.game import User
from pydantic import BaseModel, ConfigDict

from .base import BaseService


class UserExtra(BaseModel):
    collectionId: str
    collectionName: str
    created: datetime
    email: str | None = None
    emailVisibility: bool
    metadata: dict | None
    updated: datetime
    verified: bool

    model_config = ConfigDict(extra="ignore")


DBMessageUser = Literal["found", "created"]


class UserAPI(BaseService):
    async def _list(self):
        data = (await self.client.get("collections/users/records")).json()
        print(data)

    async def get_from_discord(
        self, username: str, game_name: str, game_mode: Literal["EASY", "REALISM"], discord_id: int
    ) -> tuple[User, UserExtra, DBMessageUser]:
        resp: dict = (
            await self.client.post(
                "_discord/users/from_discord",
                json={
                    "username": username,
                    "game_name": game_name,
                    "game_mode": game_mode,
                    "discord_id": discord_id,
                },
            )
        ).json()
        data = resp.get("data", {})
        u = User.from_dict(data)
        ue = UserExtra.model_validate(data)
        return u, ue, resp.get("message")

    async def update_setting(self, userid: str, key: str, value: str) -> str:
        resp: dict = (
            await self.client.put("_discord/users/edit_setting", json={"userid": userid, "update": {key: value}})
        ).json()
        return resp.get("message")
