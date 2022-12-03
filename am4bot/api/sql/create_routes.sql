CREATE TABLE IF NOT EXISTS `routes` (
  `oid` smallint unsigned NOT NULL,
  `did` smallint unsigned NOT NULL,
  `yd` smallint unsigned NOT NULL,
  `jd` smallint unsigned NOT NULL,
  `fd` smallint unsigned NOT NULL,
  `dist` float NOT NULL,
  KEY `oid_idx` (`oid`),
  KEY `did_idx` (`did`),
  KEY `yd_idx` (`yd`),
  KEY `jd_idx` (`jd`),
  KEY `fd_idx` (`fd`),
  KEY `dist_idx` (`dist`)
);