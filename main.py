from src.am4bot.config import Config
# from src.am4bot.bot import bot
import uvicorn
import asyncio

if __name__ == '__main__':
    config = Config.from_json("config.json")

    if not config.DISCORD_TOKEN or not config.AM4_API_TOKEN:
        raise AssertionError('Discord and AM4Tools token is required to run the bot!')

    # asyncio.run(bot.run(config.DISCORD_TOKEN))
    asyncio.run(
        uvicorn.run(
            "src.am4bot.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            ssl_keyfile=config.KEY_FILE,
            ssl_certfile=config.CERT_FILE,
            server_header=False
        )
    )