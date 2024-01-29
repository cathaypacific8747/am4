import httpx
from loguru import logger

from ..config import config, production


class PocketBase:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=config.PB_ENDPOINT)
        self.headers = None

    def __del__(self):
        if self.client is not None:
            self.client.aclose()

    async def login(self):
        data = (await self.client.post("/admins/auth-with-password", data={
            "identity": config.PB_EMAIL,
            "password": config.PB_PASSWORD,
        })).json()
        self.headers = {
            "Authorization": data['token'],
            "User-Agent": f"am4bot{'-dev' if not production else ''}"
        }
        
        assert self.headers is not None, "failed to login to pocketbase!"
        logger.success("logged in to pocketbase with admin id {}", data["admin"]["id"])
    
    async def list(self):
        data = (await self.client.get("collections/users/records", headers=self.headers)).json()
        print(data)




pb = PocketBase()
