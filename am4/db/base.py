import httpx


class BaseService:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
