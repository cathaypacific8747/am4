from typing import Literal, Optional

from am4.utils.game import User
from pydantic import BaseModel, ConfigDict

from .base import BaseService


class UserExtra(BaseModel):
    collectionId: str
    collectionName: str
    created: str
    email: str
    emailVisibility: bool
    metadata: dict | None
    updated: str
    verified: bool

    model_config = ConfigDict(extra="ignore")


class UserAPI(BaseService):
    async def list(self):
        data = (await self.client.get("collections/users/records")).json()
        print(data)

    async def create_from_discord(
        self, username: str, game_name: str, game_mode: Literal["EASY", "REALISM"], discord_id: int
    ) -> tuple[User, UserExtra]:
        data = (
            await self.client.post(
                "collections/users/records",
                json={
                    "username": username,
                    "verified": True,
                    "password": "password",
                    "passwordConfirm": "password",
                    "game_name": game_name,
                    "game_mode": game_mode,
                    "discord_id": discord_id,
                    "role": "USER",
                },
            )
        ).json()
        try:
            u = User.from_dict(data)
            ue = UserExtra.model_validate(data)
        except Exception:
            import traceback

            traceback.print_exc()
            raise
        return u, ue
