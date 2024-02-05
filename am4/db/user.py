from .base import BaseService


class UserAPI(BaseService):
    async def list(self):
        data = (await self.client.get("collections/users/records")).json()
        print(data)
