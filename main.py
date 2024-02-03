import logging
import os
import sys

from loguru import logger
from uvicorn import Config, Server

# from src.am4bot.bot import bot
from src.am4bot.config import config, production

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[
        {"sink": sys.stdout, "serialize": False},
        {"sink": "am4bot.log", "serialize": True},
    ])

if __name__ == '__main__':
    if not config.DISCORD_TOKEN or not config.AM4_API_TOKEN:
        raise AssertionError('Discord and AM4Tools token is required to run the bot!')

    setup_logging()
    server = Server(
        Config(
            "src.am4bot.api.main:app",
            host="127.0.0.1",
            port=8002 if production else 8001,
            reload=False if production else True,
            # ssl_keyfile=config.KEY_FILE,
            # ssl_certfile=config.CERT_FILE,
            server_header=False,
            log_level=LOG_LEVEL,
        )
    )

    server.run()
