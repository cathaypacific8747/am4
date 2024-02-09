import asyncio
from pathlib import Path

import rich
import typer

from .api.fapi import start as start_fapi
from .bot import start as start_bot
from .config import cfg, get_from_file
from .db import start as start_db
from .log import setup_logging

app = typer.Typer()
app_config = typer.Typer()
app.add_typer(app_config, name="cfg", help="config commands")


@app_config.command(name="show", help="show config")
def cfg_show():
    rich.print(cfg)
    if cfg._source is None:
        rich.print("[yellow]using default - run `am4 cfg set [path/to/config.json]!`[/yellow]")
    else:
        rich.print(f"config loaded from: {cfg._source}.")


@app_config.command(name="set", help="set config from a file")
def cfg_set(fp: Path):
    cfg_new = get_from_file(fp)
    cfg_new.save_to_internal()
    rich.print(f"succesfully set from {cfg_new._source.absolute()}.")


@app.command(help="start")
def start():
    setup_logging()

    async def main():
        db_done = asyncio.Event()

        await asyncio.gather(
            asyncio.create_task(start_db(db_done)),
            # asyncio.create_task(start_fapi(db_done)),
            asyncio.create_task(start_bot(db_done)),
        )

    asyncio.run(main())


app()
