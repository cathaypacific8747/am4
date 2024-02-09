import httpx
from loguru import logger

from ..config import cfg
from .user import UserAPI


class PocketBase:
    def __init__(self, endpoint: str = cfg.db.PB_ENDPOINT) -> None:
        self.client = httpx.AsyncClient(
            base_url=endpoint,
            headers={"User-Agent": "am4-db"},
        )
        self._user_api = UserAPI(self.client)

    async def _login_admin(self, identity: str = cfg.db.PB_EMAIL, password: str = cfg.db.PB_PASSWORD):
        data = (
            await self.client.post(
                "/admins/auth-with-password",
                data={
                    "identity": identity,
                    "password": password,
                },
            )
        ).json()
        if "token" not in data:
            raise Exception("failed to login to pocketbase!")
        self.client.headers.update(
            {
                "Authorization": data["token"],
            }
        )
        logger.success("db client connection started with admin.id={}!", data["admin"]["id"])

    @property
    def users(self):
        return self._user_api


pb = PocketBase()
