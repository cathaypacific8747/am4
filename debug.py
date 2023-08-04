import asyncio
import am4utils
from am4utils.db import init
from am4utils.game import AllianceCache
from am4utils.game.api import fetch_alliance, fetch_user
from src.am4bot.config import Config

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')

    init()

    config = Config.from_json("config.json")
    async def main():
        status, cache = await fetch_alliance(None)
        print(cache.id)

    asyncio.run(main())