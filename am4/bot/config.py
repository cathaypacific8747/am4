from ..config import ConfigBase, production


class Config(ConfigBase):
    DISCORD_TOKEN: str = ""
    AM4_API_TOKEN: str = ""
    COMMAND_PREFIX: str = "$"
    DEBUG_CHANNELID: int = 0
    BOTSPAM_CHANNELID: int = 0
    PRICEALERT_CHANNELID: int = 0
    PRICEALERT_ROLEID: int = 0
    MODERATOR_ROLEID: int = 0
    HELPER_ROLEID: int = 0


config = Config.from_json("config.production.json" if production else "config.json")
