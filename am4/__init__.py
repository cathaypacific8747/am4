import logging
import os

from uvicorn import Config, Server

from .config import production

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))

api_server = Server(
    Config(
        "api.main:app",
        host="127.0.0.1",
        port=8002 if production else 8001,
        reload=False if production else True,
        # ssl_keyfile=config.KEY_FILE,
        # ssl_certfile=config.CERT_FILE,
        server_header=False,
        log_level=LOG_LEVEL,
    )
)
