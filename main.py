from src.am4bot.config import Config
from src.am4bot.main import bot

if __name__ == '__main__':
    config = Config.from_json("config.json")

    if not config.DISCORD_TOKEN or not config.AM4_API_TOKEN:
        raise AssertionError('Discord and AM4Tools token is required to run the bot!')

    bot.run(config.DISCORD_TOKEN)