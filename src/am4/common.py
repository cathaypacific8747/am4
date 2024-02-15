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
HELP_ACRO_CFG = (
    "[Optional] **Aircraft configuration algorithm**: one of `AUTO`, `FJY`, `FYJ`, `JFY`, `JYF`, `YFJ`, `YJF`"
    " (pax/vip aircraft), or `AUTO`, `L`, `H` (cargo aircraft). If not specified, `AUTO` is used, "
    "which selects the best order for that distance class."
)
HELP_ACRO_MAXDIST = "[Optional] **Maximum route distance (km)** - defaults to 6371π if not specified."
HELP_ACRO_MAXFT = "[Optional] **Maximum flight time (h)** - defaults to 24 if not specified."
HELP_ACRO_TPD_MODE = (
    "[Optional] **Trips per day mode**: one of `AUTO`, `AUTO_MULTIPLE_OF`, `STRICT`. If not specified, "
    "`AUTO` is used, which finds the optimal trips_per_day through brute-force."
)
HELP_ACRO_TPD = (
    "[Optional] **Trips per day**: defaults to 1. Note that this parameter is only respected when tpd_mode is set "
    "to `AUTO_MULTIPLE_OF` or `STRICT`. When `tpd_mode=AUTO`, it throws an error."
)
