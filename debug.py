import asyncio
import am4utils
from am4utils.db import init
from am4utils.game import AllianceLog
from am4utils.game.api import fetch_alliance, fetch_user
from src.am4bot.config import Config

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')

    init()

    config = Config.from_json("config.json")
    async def main():
        status, log = await fetch_alliance(None, "src/am4utils/tests/data/A_Valiant Air_1691065293.json")
        # print(log.log_id, log.name, len(log.members))
        # log2 = AllianceLog.from_log_id(log.log_id)
        # print(log2.log_id, log2.name, len(log2.members))

    asyncio.run(main())