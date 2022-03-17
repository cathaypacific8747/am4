# V3

A modern rewrite of the discord bot.

```
$ sudo apt-get update
$ sudo apt-get install postgresql
$ sudo passwd postgres
$ sudo service postgresql start
$ sudo -u postgres psql
postgres-# ALTER USER postgres WITH PASSWORD 'XXX';
postgres-# CREATE DATABASE am4bot;
postgres-# \q
$ cp .env.template .env
```

Edit `.env` accordingly.