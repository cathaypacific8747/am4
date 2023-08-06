import asyncio
import am4utils
from am4utils.db import init
from am4utils.game import AllianceLog
from am4utils.game.api import fetch_alliance, fetch_user
from src.am4bot.config import Config
# from am4utils.airport import Airport

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')

    init()

    # apsr = Airport.search('fullname:hong kong, hong kong')
    # print(apsr.parse_result.search_str)
    # print(apsr.ap.iata, apsr.ap.icao, apsr.ap.name, apsr.ap.country)
    # raise SystemExit

    config = Config.from_json("config.json")
    async def main():
        # status, log = await fetch_alliance(None, "src/am4utils/tests/data/A_Valiant Air_1691065293.json")
        # print(log.log_id, log.name, len(log.members))
        # log2 = AllianceLog.from_log_id(log.log_id)
        # print(log2.log_id, log2.name, len(log2.members))
        
        status, log = await fetch_user(None, "src/am4utils/tests/data/U_Maxy Air_1680180000.json")
        print(log.username)
        print(log.share_log[0].ts, log.share_log[0].share)
        print(log.share_log[-1].ts, log.share_log[-1].share)
        print(log.awards[0].ts, log.awards[0].award)

    asyncio.run(main())