# am4utils

Tools and utilities for Airline Manager 4 bot.

Supports Python 3.9 - 3.11 on the following platforms:
- manylinux2_28 x86_64 (ubuntu 18.04+, debian 10+, fedora 30+)
- windows amd64
- macos x86_64 / amd64

### Database tests
download the [DuckDB command line binaries](https://duckdb.org/docs/installation/)

```sql
CREATE TABLE IF NOT EXISTS users (
  id                UUID NOT NULL DEFAULT uuid(),
  username          VARCHAR NOT NULL DEFAULT '',
  password          VARCHAR NOT NULL DEFAULT '',
  game_id           UBIGINT NOT NULL DEFAULT 0,
  game_name         VARCHAR NOT NULL DEFAULT '',
  game_mode         BOOLEAN NOT NULL DEFAULT FALSE,
  discord_id        UBIGINT NOT NULL DEFAULT 0,
  wear_training     UTINYINT NOT NULL DEFAULT 0,
  repair_training   UTINYINT NOT NULL DEFAULT 0,
  l_training        UTINYINT NOT NULL DEFAULT 0,
  h_training        UTINYINT NOT NULL DEFAULT 0,
  fuel_training     UTINYINT NOT NULL DEFAULT 0,
  co2_training      UTINYINT NOT NULL DEFAULT 0,
  fuel_price        USMALLINT NOT NULL DEFAULT 700,
  co2_price         UTINYINT NOT NULL DEFAULT 120,
  accumulated_count USMALLINT NOT NULL DEFAULT 0,
  load              DOUBLE NOT NULL DEFAULT 87,
  role              UTINYINT NOT NULL DEFAULT 0,
);
CREATE INDEX IF NOT EXISTS users_idx ON users(id, username, game_id, game_name, discord_id);
```