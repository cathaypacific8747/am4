USE `am4bot`;
CREATE TABLE `guilds` (
	`id` mediumint NOT NULL AUTO_INCREMENT COMMENT 'internal id',
	`guild_id` bigint NOT NULL COMMENT 'discord guild id',
	`prefix` CHAR(50) NOT NULL DEFAULT '$' COMMENT 'command prefix',
	`easy_role_id` bigint NULL DEFAULT NULL COMMENT 'role id of easy users',
	`realism_role_id` bigint NULL DEFAULT NULL COMMENT 'role id of realism users',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `guild_id` (`guild_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;