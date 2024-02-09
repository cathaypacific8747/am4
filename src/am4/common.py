HELP_AP_ARG0 = """**Search query for airport** (case-insensitive).
Examples: `id:3500`, `iata:Hkg`, `icao:vHHH`, `name:hong kong`, `VHHH`"""
HELP_AC_ARG0 = """**Search query for aircraft** (case insensitive).
Examples: `b744`, `B747-400`, `id:1`, `shortname:b744`, `name:B747-400`, `b744[1]`, `b744[1,sfc]`, `b744[3,s,f,x]`.
Characters inside square brackets denote engine options:
- `s` for 1.1x **s**peed
- `f` for 0.9x **f**uel
- `c` for 0.9x **C**O2
- `x` for 4**x** speed.
By default, the fastest engine option is used (priority 0).
For slower engine options, specify the engine option in the query.
"""
