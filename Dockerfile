FROM python:3.11-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential

WORKDIR /app
ADD . /app
EXPOSE 8002 8090

RUN python3 -m pip install ".[dev,api,bot]" && \
    python3 -c "from am4.utils.db import init; init()" && \
    python3 -c "from src.am4.db import ensure_pb_exists; ensure_pb_exists()"

CMD python3 -m src.am4 start api