from pathlib import Path

import orjson
from pydantic import BaseModel

_cfg_internal_fp = Path(__file__).parent / ".config.json"


class ConfigDB(BaseModel):
    PB_ENDPOINT: str = "http://127.0.0.1:8090/api/"
    PB_EMAIL: str = "admin@localhost"
    PB_PASSWORD: str = "am4"


class ConfigAPI(BaseModel):
    HOST: str = "127.0.0.1"
    PORT: int = 8002
    RELOAD: bool = True


class ConfigBot(BaseModel):
    DISCORD_TOKEN: str
    OFFICIAL_API_TOKEN: str
    COMMAND_PREFIX: str = "$"
    DEBUG_CHANNELID: int
    BOTSPAM_CHANNELID: int
    PRICEALERT_CHANNELID: int
    PRICEALERT_ROLEID: int
    MODERATOR_ROLEID: int
    HELPER_ROLEID: int


class Config(BaseModel):
    db: ConfigDB = ConfigDB()
    api: ConfigAPI = ConfigAPI()
    bot: ConfigBot | None = None
    LOG_LEVEL: str = "DEBUG"
    JSON_LOGS: bool = False
    DEBUG: bool = False
    _source: Path | None = None

    def save_to_internal(self):
        with open(_cfg_internal_fp, "w") as f:
            f.write(self.model_dump_json(indent=4))


def get_from_file(fp: Path) -> Config:
    with open(fp, "r") as f:
        cfg = Config(**orjson.loads(f.read()))
        cfg._source = fp
        return cfg


cfg = get_from_file(_cfg_internal_fp) if _cfg_internal_fp.exists() else Config()
