class Config:
    DISCORD_TOKEN: str = ''
    AM4_API_TOKEN: str = ''
    COMMAND_PREFIX: str = '$'
    DEBUG_CHANNELID: int = 0
    BOTSPAM_CHANNELID: int = 0
    PRICEALERT_CHANNELID: int = 0
    PRICEALERT_ROLEID: int = 0
    MODERATOR_ROLEID: int = 0
    HELPER_ROLEID: int = 0
    
    def __init__(self, cfg: dict):
        self.__dict__.update(cfg)

    @classmethod
    def from_json(cls, fn: str):
        import json
        with open(fn) as f:
            return cls(json.load(f))