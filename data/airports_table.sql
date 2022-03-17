CREATE TABLE airports (
	id SMALLINT NOT NULL PRIMARY KEY,
	iata VARCHAR NOT NULL,
	icao VARCHAR NOT NULL,
	runway SMALLINT NOT NULL,
	market SMALLINT NOT NULL,
	lat DOUBLE PRECISION NOT NULL,
	lng DOUBLE PRECISION NOT NULL,
	city VARCHAR NOT NULL,
	country VARCHAR NOT NULL
);

CREATE UNIQUE INDEX id ON airports(id);
CREATE UNIQUE INDEX iata_idx ON airports(iata);
CREATE UNIQUE INDEX icao_idx ON airports(icao);
CREATE INDEX runway_idx ON airports(runway);
CREATE INDEX market_idx ON airports(market);
CREATE INDEX city_idx ON airports(city);
CREATE INDEX country_idx ON airports(country);