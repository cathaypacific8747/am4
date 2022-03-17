CREATE TABLE aircrafts (
	id SMALLINT NOT NULL PRIMARY KEY,
	model VARCHAR NOT NULL UNIQUE,
	type SMALLINT NOT NULL,
	manufacturer VARCHAR NOT NULL,
	shortname VARCHAR NOT NULL UNIQUE,
	capacity INTEGER NOT NULL,
	runway SMALLINT NOT NULL,
	a_check INTEGER NOT NULL,
	range SMALLINT NOT NULL,
	ceil INTEGER NOT NULL,
	maintenance SMALLINT NOT NULL,
	price INTEGER NOT NULL,
	pilots SMALLINT NOT NULL,
	crew SMALLINT NOT NULL,
	engineers SMALLINT NOT NULL,
	tech SMALLINT NOT NULL,
	thumb VARCHAR NOT NULL
);

CREATE UNIQUE INDEX id_idx ON aircrafts(id);
CREATE UNIQUE INDEX model_idx ON aircrafts(model);
CREATE UNIQUE INDEX shortname_idx ON aircrafts(shortname);
CREATE INDEX type_idx ON aircrafts(type);
CREATE INDEX manufacturer_idx ON aircrafts(manufacturer);
CREATE INDEX capacity_idx ON aircrafts(capacity);
CREATE INDEX runwayreq_idx ON aircrafts(runway);
CREATE INDEX range_idx ON aircrafts(range);
CREATE INDEX price_idx ON aircrafts(price);