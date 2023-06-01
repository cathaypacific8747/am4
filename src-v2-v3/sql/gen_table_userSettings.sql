USE `am4bot`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` mediumint NOT NULL AUTO_INCREMENT COMMENT 'internal',
  `discord_id` bigint unsigned DEFAULT NULL COMMENT 'Discord userId',
  `game_id` int unsigned DEFAULT NULL COMMENT 'AM4 userId',
  `ign` char(100) DEFAULT NULL COMMENT 'AM4 name',
  -- details below
  `mode` enum('e','r','unknown') DEFAULT 'unknown' COMMENT 'AM4 gamemode',
  `pax_mode` enum('y','f','brute') DEFAULT 'brute' COMMENT 'y,f: y,f-class priority; brute: brute force',
  `cargo_mode` enum('l','brute') DEFAULT 'l' COMMENT 'l: l-class priority; brute: brute-force',
  `large_training` tinyint unsigned DEFAULT '0' COMMENT '0-6',
  `heavy_training` tinyint unsigned DEFAULT '0' COMMENT '0-6',
  `fuel_price` smallint unsigned DEFAULT '850' COMMENT '0-3000',
  `co2_price` smallint unsigned DEFAULT '130' COMMENT '0-200',
  `fuel_training` tinyint unsigned DEFAULT '0' COMMENT '0-3',
  `co2_training` tinyint unsigned DEFAULT '0' COMMENT '0-5',
  `use_estimation` tinyint DEFAULT '1' COMMENT 'whether to use estimation',
  `reputation` tinyint unsigned DEFAULT '100' COMMENT '0-100',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `discord_id` (`discord_id`) USING BTREE,
  INDEX `game_id` (`game_id`) USING BTREE,
  INDEX `ign` (`ign`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;