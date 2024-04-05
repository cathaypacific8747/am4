This tutorial shows you how to quickly host your own instance of AM4 bot using Docker.

**Requirements**:

- OS: Linux/Windows/MacOS
- RAM: 4GB
- Disk space: 1GB
- [Docker](https://docs.docker.com/get-docker/)

If you are on Windows, it is recommended to use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) alongside Docker.

## Installation

Clone the repository and run inside:
```sh
docker build -t am4 .
docker run -d -p 8002:8002 -p 8090:8090 --name am4-dev am4
# sudo docker exec -it am4-dev bash
```
Access the API docs at `localhost:8002/docs` and database admin UI at `localhost:8090/_`.

### Bot
If you would also like to run the discord bot, you must load your custom configuration file ([more info](./discord-bot.md#configuration-file)):
```sh
docker run -d -p 8002:8002 -p 8090:8090 --name am4-dev am4 tail -f /dev/null
mv config.example.json config.json
# edit config.json
docker cp config.json am4-dev:/app/config.json
docker exec am4-dev python3 -m src.am4 cfg set config.json
docker exec -d am4-dev python3 -m src.am4 start api,bot
```