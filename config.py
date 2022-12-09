class Config:
    discord_token: str = ""
    debug_channelId: int = 0
    botSpam_channelId: int = 0
    priceAlert_channelId: int = 0
    priceAlert_roleId: int = 0
    moderator_roleId: int = 0
    helper_roleId: int = 0
    db_host: str = ""
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_database: str = ""
    db_odbc_copy_ini: bool = True
    
    def __init__(self, cfg: dict):
        self.__dict__.update(cfg)

    @classmethod
    def from_json(cls, fn: str):
        import json
        with open(fn) as f:
            return cls(json.load(f))

config = Config.from_json("config.json")