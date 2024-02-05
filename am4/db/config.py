from ..config import ConfigBase, production


class Config(ConfigBase):
    PB_ENDPOINT: str = "http://127.0.0.1:8090/api/"
    PB_EMAIL: int = 0
    PB_PASSWORD: int = 0


config = Config.from_json("config.production.json" if production else "config.json")
