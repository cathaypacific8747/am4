import asyncio
import os
import pathlib
import zipfile
from io import BytesIO

import httpx
from loguru import logger

from ..config import cfg
from .client import pb

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


async def _create_admin():
    args = [str(base_path / "pocketbase"), "admin", "create", cfg.db.PB_EMAIL, cfg.db.PB_PASSWORD]
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        data = line.decode().strip()
        if "Successfully created new admin" in data:
            logger.success(data)
        elif "UNIQUE constraint failed" in data:
            logger.info("admin already exists, creation skipped")
        else:
            logger.info(data)


async def start(db_done: asyncio.Event):
    ensure_pb_exists()
    logger.info(f"Starting PocketBase at {cfg.db.PB_HOST}...")
    args = [str(base_path / "pocketbase"), "serve", f"--http={cfg.db.PB_HOST}"]
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        data = line.decode().strip()
        if "Server started" in data:
            logger.success(data)
            await _create_admin()
            await pb._login_admin()
            db_done.set()
        elif "Error" in data:
            logger.error(data)
            break
        else:
            logger.debug(data)
