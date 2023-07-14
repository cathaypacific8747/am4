# ![logo](src/am4bot/assets/img/logo-small.png) am4bot

[![](https://dcbadge.vercel.app/api/server/4tVQHtf?style=flat)](https://discord.gg/4tVQHtf) [![CI](https://github.com/cathaypacific8747/am4bot/actions/workflows/ci.yml/badge.svg)](https://github.com/cathaypacific8747/am4bot/actions/workflows/ci.yml)

A discord bot for the game [Airline Manager 4](airlinemanager.com), used on our [server](https://discord.gg/4tVQHtf).

Our bot is currently running legacy code in the [`src-old`](./src-old/) directory - I am now rewriting the core calculations in C++ for better performance under [`src/am4utils`](./src/am4utils/), with the main bot written in Python under [`src/am4bot (under construction)`](./src/am4bot/). The backend for [am4help.com](https://am4help.com/) is developed in a separate repository and can be found [here](https://github.com/br-tsilva/api.am4tools.com) instead.

## Current Features
- calculates essential statistics
    - most distance-efficient stopovers
    - route demands, best seat configurations, best ticket prices, estimated income
    - player rank, mode, achievements, fleet
    - alliance rank, share value, contribution
    - aircraft characteristics and profit
    - airport characteristics
- CSV export for route queries
- fuel/CO2 notifications
- aircraft characteristics comparisons
- internal *Star Alliance* tools (now disbanded)
    - adding competitor alliances to watchlist
    - alliance comparisons over time: value, contribution/day, rate of changes
    - realtime alliance-member comparisons: SV/contribution distribution
    - member tracking: cheat detection tools, departure pattern identification

## AM4Utils Development
Requirements: python3.9+, C++17 compliant compiler

```bash
# windows
virtualenv .venv
.venv\Scripts\activate

# linux
sudo apt install build-essential python3-dev
virtualenv .venv
source .venv/bin/activate

# C++ main dev
mkdir build
cd build
cmake .. && cmake --build . --target _core_executable && ./_core_executable

# python dev
pip3 install --verbose "src/am4utils/.[dev]"
pytest
cd src/am4utils
python3 generate-stubs.py
pip3 uninstall am4utils -y

# build wheel
mkdir wheelhouse
python3 -m pip wheel . --wheel-dir=wheelhouse no-deps -v
pip install wheelhouse/am4utils-*.whl --force-reinstall

.venv/scripts/deactivate
```

## AM4 Bot development
```bash
sudo apt install libnss3-tools
curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
chmod +x mkcert-v*-linux-amd64
sudo cp mkcert-v*-linux-amd64 /usr/local/bin/mkcert
pip3 install --verbose ".[dev]"

rsync -avzo 
```

## Commands

### Public
- `$route|stop <airport> <airport> <aircraft> [flights_per_day] [reputation]`: finds the best route between two airports
  
  ![route](src/am4bot/assets/img/route.png)
- `$routes <airport> <aircraft> <max_distance> <flights_per_day> [reputation]`: finds the best destinations from a certain airport, sorted by decreasing estimated income
  
  ![routes](src/am4bot/assets/img/routes.png)
- `$user [player]`: shows player (and associated alliance if found) statistics
  
  ![user](src/am4bot/assets/img/user.png)
- `$fleet [player]`: shows player fleet and estimated income
  
  ![fleet](src/am4bot/assets/img/fleet.png)
- `$info <aircraft>`: shows basic aircraft information and rough profit estimations
  
  ![info](src/am4bot/assets/img/info.png)
- `$compare <aircraft>`: compares two aircrafts
  
  ![compare](src/am4bot/assets/img/compare.png)
- `$search <aircraft>`: finds the associated aircraft shortname for aircraft commands
  
  ![search](src/am4bot/assets/img/search.png)
- `$airport <airport>`: shows airport information
  
  ![airport](src/am4bot/assets/img/airport.png)
- `$price f[fuel_price] c[co2_price]`: notifies everyone for the fuel price
  
  ![price](src/am4bot/assets/img/price.png)

### Internal Alliance Tools
- `$memberCompare <player> <player>`: compares descending structure of contribution/day and SV
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$alliance <alliance>`: shows AV progression and d(AV)/dt.
  
  ![alliance](src/am4bot/assets/img/alliance.png)
- `$allianceCompare <alliance> <alliance>`: compares AV progression and gap difference over time, shows 48h/12h-average contribution/day graphs
  
  ![alliance-compare](src/am4bot/assets/img/alliance-compare.png)
- `$member <player> [player[]]` shows contribution/day, total contribution and SV history for 1+ members
  
  ![member](src/am4bot/assets/img/member.png)
- `$actions <player> [maxResults]`: shows log of estimated departures, contributions and income
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$watchlist [add|+, remove|rm|-] [alliance]`: shows, adds or remove alliance(s) to the watchlist