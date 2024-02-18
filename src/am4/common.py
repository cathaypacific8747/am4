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
HELP_U_WEAR_TRAINING = "**Wear training** (default: `0`)"
HELP_U_REPAIR_TRAINING = "**Repair training** (default: `0`)"
HELP_U_L_TRAINING = "**L training** (default: `0`)"
HELP_U_H_TRAINING = "**H training** (default: `0`)"
HELP_U_FUEL_TRAINING = "**Fuel training** (default: `0`)"
HELP_U_CO2_TRAINING = "**CO2 training** (default: `0`)"
HELP_U_FUEL_PRICE = "**Fuel price** (default: `700`)"
HELP_U_CO2_PRICE = "**CO2 price** (default: `120`)"
HELP_U_ACCUMULATED_COUNT = "**Accumulated fleet count**, used for marketing cost estimation (default: `0`)"
HELP_U_FOURX = (
    "**4x** (default: `false`).\n"
    "*Note*: if this is set in the aircraft options (e.g. `a388[x]`), it'll take precendence"
)
HELP_U_INCOME_LOSS_TOL = (
    "**Income loss tolerance** (default: `0.0`)\n"
    "During end-game, hub availability becomes an issue and you might want to cram in more aircraft per route, "
    "even if that means losing some income.\nThe algorithm will perform the cramming for you, "
    "and stop *immediately* if the income drops below the maximum.\n"
    "But that'll mean wasting lots of precious demand. If you set this to, say `0.1`, the income per flight will be 90%"
    "of the max, but in exchange you can cram in more aircraft per hub and gain more income.\n"
    "**Recommended: set this to `0.1` for end-game players**"
)
HELP_U_LOAD = (
    "**Assumed aircraft load** (default: `0.87`)\n\n"
    "`0.87` means 87% of the aircraft is filled: demand will be 'virtually' inflated by 1/0.87 = +14.9%.\n"
    "*Note*: you can assume this to be roughly equivalent to the reputation."
)
