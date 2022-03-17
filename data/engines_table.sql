CREATE TABLE engines (
	aircraft_id SMALLINT NOT NULL,
	name VARCHAR NOT NULL,
	speed SMALLINT NOT NULL,
	fuel REAL NOT NULL,
	co2 REAL NOT NULL
);

CREATE INDEX aircraft_id_idx ON engines(aircraft_id);
CREATE INDEX name_idx ON engines(name);
CREATE INDEX speed_idx ON engines(speed);
CREATE INDEX fuel_idx ON engines(fuel);
CREATE INDEX co2_idx ON engines(co2);