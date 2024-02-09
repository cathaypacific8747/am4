import asyncio
import os
import pathlib
import zipfile
from io import BytesIO

import httpx
from loguru import logger

PB_VERSION = "0.21.1"
base_path = pathlib.Path(__file__).parent


def ensure_pb_exists():
    if (base_path / "pocketbase").exists():
        return
    logger.warning("pocketbase not found, downloading...")
    data = BytesIO(
        httpx.get(
            f"https://github.com/pocketbase/pocketbase/releases/download/v{PB_VERSION}/pocketbase_{PB_VERSION}_linux_amd64.zip",
            follow_redirects=True,
        ).content
    )
    with zipfile.ZipFile(data) as z:
        z.extract("pocketbase", base_path)
    os.chmod(str(base_path / "pocketbase"), 0o755)


async def run_server(db_done: asyncio.Event):
    ensure_pb_exists()
    logger.info("Starting PocketBase...")
    process = await asyncio.create_subprocess_exec(
        str(base_path / "pocketbase"),
        "serve",
        # "--dev",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        data = line.decode().strip()
        if "Server started" in data:
            db_done.set()
            logger.success(data)
        elif "Error" in data:
            logger.error(data)
            break
