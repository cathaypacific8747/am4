from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from discord.ext import commands

from .errors import AircraftNotFoundError, AirportNotFoundError


class AirportCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> Airport.SearchResult:
        acsr = Airport.search(query)

        if not acsr.ap.valid:
            raise AirportNotFoundError(acsr)
        return acsr


class AircraftCvtr(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> Aircraft.SearchResult:
        acsr = Aircraft.search(query)

        if not acsr.ac.valid:
            raise AircraftNotFoundError(acsr)
        return acsr
