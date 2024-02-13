# ![logo](src/am4/bot/assets/img/logo-small.png) am4

[![](https://dcbadge.vercel.app/api/server/4tVQHtf?style=flat)](https://discord.gg/4tVQHtf) [![CI](https://github.com/cathaypacific8747/am4/actions/workflows/ci.yml/badge.svg)](https://github.com/cathaypacific8747/am4/actions/workflows/ci.yml)

[Airline Manager 4](https://airlinemanager.com) is an online multiplayer game whose goal is to build an airline from scratch. Rapid progression in the game requires thorough market research and route planning to high demand destinations, while considering recurring fuel/CO2 costs, and conforming to aircraft range/runway requirement constraints.

The weekly leaderboards and alliances are highly competitive arenas which require extensive knowledge in the game: this repository contains a set of high-performance foundational tools, built for the more technical-oriented players. The project is structured as follows:
- [x] core calculations written in C++ for exhaustive searches ([`src/am4/utils`](./src/am4/utils))
- [x] a Python web API exposing the core ([`src/am4/api`](./src/am4/api/))
- [x] an sqlite database storing user settings ([`src/am4/db`](./src/am4/db/)) 
- [x] a Python discord bot for our community ([`src/am4/bot`](./src/am4/bot/))
- [ ] [`am4help.com`](https://am4help.com/): a SolidJS frontend calling the API (under construction, [`src/am4/web`](./src/am4/web/))

<div align="center">
  <img src="src/am4/bot/assets/img/overview.drawio.svg" alt="overview">
</div>

> [!WARNING]
> The code here represents my journey of learning various programming languages: parts of it are poorly written. Feel free to contribute by opening issues or pull requests!

## Usage
The easiest way to get started is [Docker](https://docs.docker.com/get-docker/).

Clone the repository and run:
```sh
docker build -t am4 .
docker run -d -p 8002:8002 -p 8090:8090 --name am4-dev am4
# sudo docker exec -it am4-dev bash
```
Access the API docs at `localhost:8002/docs` and database admin UI at `localhost:8090/_`.

If you would also like to run the discord bot, you must load your custom configuration file ([more info](#configuration-file)):
```sh
docker run -d -p 8002:8002 -p 8090:8090 --name am4-dev am4 tail -f /dev/null
mv config.example.json config.json
# edit config.json
docker cp config.json am4-dev:/app/config.json
docker exec am4-dev python3 -m src.am4 cfg set config.json
docker exec -d am4-dev python3 -m src.am4 start api,bot
```
## Development
If you are using VSCode, install the recommended extensions and use Tasks instead of manually executing the commands.

### Core Utils
The [core utils](./src/am4/utils/) is the most important part of the project, as it is used by the [API](#web-api), [bot](#discord-bot) and [web](#web-frontend).
#### Modifying it
The main entry point is the [debug executable](./src/am4/utils/cpp/main.cpp).

A C++17 compliant compiler and Linux system is required to build it.

> [!TIP]
> VSCode users: set build target and launch.

```sh
sudo apt-get install build-essential
# optionally install vtune for profiling

cd src/am4/utils
mkdir build
cd build
cmake .. && cmake --build . --target _core_executable && ./_core_executable
```
Note that the `BUILD_PYBIND` definition/directives controls whether the pybind11 bindings are included. It is set to 0 when building the executable.

#### Create the Python bindings
> [!TIP]
> VSCode users: run the `py: reinstall` task.

```sh
# in root dir:
sudo apt-get install python3-dev python3-pip
pip3 install virtualenv
virtualenv .venv
source .venv/bin/activate

pip3 install --verbose ".[dev,api,bot]" --config-settings=cmake.define.COPY_DATA=1
pytest
cd src/am4/utils
python3 generate-stubs.py
# pip3 uninstall src/am4/utils -y
```

The `am4` package and data files will then be installed in your site-packages, ready for use:
```py
from am4.utils.db import init
from am4.utils.aircraft import Aircraft
init() # IMPORTANT: loads the aircraft, airport and routes etc.
a = Aircraft.search("b744")
print(a.ac)
```
To learn more on how to use it, check out the [tests](./src/am4/utils/tests/) or the [generated stubs](./src/am4/utils/stubs/utils/).

### Configuration File
The database and API can run out of the box without any configuration file, by using the [defaults](./src/am4/config.py). However, running the discord bot/building the frontend will require you to provide custom config.

To do this, rename `./config.example.json` to `./config.json` and modify it. Then, run:
```sh
python3 -m src.am4 cfg set config.json
```
This will verify and persist the settings to `./src/am4/.config.json`, which is used in future calls.

### Database
User authentication is handled by [pocketbase](https://github.com/pocketbase/pocketbase), a lightweight SQLite-based backend supporting OAuth2.0.

It is automatically started before the API/discord bot when using the CLI.

### Web API
The core utils are exposed to the web using [FastAPI](https://github.com/tiangolo/fastapi). Validation on query params/body is handled by [Pydantic](https://github.com/pydantic/pydantic) models defined under [`./src/am4/db/models`](./src/am4/db/models/).

To start it, use:
```sh
python3 -m src.am4 start api
```

### Discord bot
It is similar to the API in design, but is more sophisticated in that it reads users' roles to determine their game mode.

To start it, use:
```sh
python3 -m src.am4 start bot
```

### Web Frontend
Under construction!


## Documentation for Legacy Code
- `src-old`: the very first iteration of the discord bot.
- `src-v2-v3`: my first attempts at rewriting in C/Cython
- `research`: parts of my attempts to figure out the demand formula

### Features
Old bot:
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
  - alliance comparisons over time: value,contribution/day, rate of changes
  - realtime alliance-member comparisons: SV/contribution distribution
  - member tracking: cheat detection tools, departure pattern identification

### Public
- `$route|stop <airport> <airport> <aircraft> [flights_per_day] [reputation]`: finds the best route between two airports
  
  ![route](src/am4/bot/assets/img/route.png)
- `$routes <airport> <aircraft> <max_distance> <flights_per_day> [reputation]`: finds the best destinations from a certain airport, sorted by decreasing estimated income
  
  ![routes](src/am4/bot/assets/img/routes.png)
- `$user [player]`: shows player (and associated alliance if found) statistics
  
  ![user](src/am4/bot/assets/img/user.png)
- `$fleet [player]`: shows player fleet and estimated income
  
  ![fleet](src/am4/bot/assets/img/fleet.png)
- `$info <aircraft>`: shows basic aircraft information and rough profit estimations
  
  ![info](src/am4/bot/assets/img/info.png)
- `$compare <aircraft>`: compares two aircrafts
  
  ![compare](src/am4/bot/assets/img/compare.png)
- `$search <aircraft>`: finds the associated aircraft shortname for aircraft commands
  
  ![search](src/am4/bot/assets/img/search.png)
- `$airport <airport>`: shows airport information
  
  ![airport](src/am4/bot/assets/img/airport.png)
- `$price f[fuel_price] c[co2_price]`: notifies everyone for the fuel price
  
  ![price](src/am4/bot/assets/img/price.png)

### Internal Alliance Tools
- `$memberCompare <player> <player>`: compares descending structure of contribution/day and SV
  
  ![member-compare](src/am4/bot/assets/img/member-compare.png)
- `$alliance <alliance>`: shows AV progression and d(AV)/dt.
  
  ![alliance](src/am4/bot/assets/img/alliance.png)
- `$allianceCompare <alliance> <alliance>`: compares AV progression and gap difference over time, shows 48h/12h-average contribution/day graphs
  
  ![alliance-compare](src/am4/bot/assets/img/alliance-compare.png)
- `$member <player> [player[]]` shows contribution/day, total contribution and SV history for 1+ members
  
  ![member](src/am4/bot/assets/img/member.png)
- `$actions <player> [maxResults]`: shows log of estimated departures, contributions and income
  
  ![member-compare](src/am4/bot/assets/img/member-compare.png)
- `$watchlist [add|+, remove|rm|-] [alliance]`: shows, adds or remove alliance(s) to the watchlist