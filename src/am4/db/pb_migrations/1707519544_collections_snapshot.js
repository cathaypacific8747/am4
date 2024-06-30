/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const snapshot = [
    {
      "id": "_pb_users_auth_",
      "created": "2024-02-03 13:18:53.989Z",
      "updated": "2024-02-09 22:58:44.859Z",
      "name": "users",
      "type": "auth",
      "system": false,
      "schema": [
        {
          "system": false,
          "id": "users_name",
          "name": "game_name",
          "type": "text",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": null,
            "max": null,
            "pattern": ""
          }
        },
        {
          "system": false,
          "id": "0v5iz2wb",
          "name": "game_id",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": null,
            "max": null,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "msuzdgf4",
          "name": "game_mode",
          "type": "select",
          "required": true,
          "presentable": false,
          "unique": false,
          "options": {
            "maxSelect": 1,
            "values": [
              "EASY",
              "REALISM"
            ]
          }
        },
        {
          "system": false,
          "id": "olpcbglt",
          "name": "discord_id",
          "type": "number",
          "required": true,
          "presentable": false,
          "unique": false,
          "options": {
            "min": null,
            "max": null,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "ygfo2boo",
          "name": "wear_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 5,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "kykcfa8g",
          "name": "repair_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 5,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "0apead8g",
          "name": "l_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 6,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "iu3kipez",
          "name": "h_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 6,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "xuqkex6d",
          "name": "fuel_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 3,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "tpdyxiek",
          "name": "co2_training",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 5,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "iy24mxi6",
          "name": "fuel_price",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 3000,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "anioiqnp",
          "name": "co2_price",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 200,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "cbsbwtni",
          "name": "accumulated_count",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 65535,
            "noDecimal": true
          }
        },
        {
          "system": false,
          "id": "wrllnkkg",
          "name": "load",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 1,
            "noDecimal": false
          }
        },
        {
          "system": false,
          "id": "1tnjcpie",
          "name": "income_loss_tol",
          "type": "number",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "min": 0,
            "max": 1,
            "noDecimal": false
          }
        },
        {
          "system": false,
          "id": "6mxyhve7",
          "name": "fourx",
          "type": "bool",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {}
        },
        {
          "system": false,
          "id": "pxxrhh3x",
          "name": "role",
          "type": "select",
          "required": true,
          "presentable": false,
          "unique": false,
          "options": {
            "maxSelect": 1,
            "values": [
              "BANNED",
              "USER",
              "TRUSTED_USER",
              "TOP_ALLIANCE_MEMBER",
              "TOP_ALLIANCE_ADMIN",
              "HELPER",
              "MODERATOR",
              "ADMIN",
              "GLOBAL_ADMIN"
            ]
          }
        },
        {
          "system": false,
          "id": "cq4myxa2",
          "name": "metadata",
          "type": "json",
          "required": false,
          "presentable": false,
          "unique": false,
          "options": {
            "maxSize": 2000000
          }
        }
      ],
      "indexes": [
        "CREATE INDEX `idx_dqv0lYm` ON `users` (\n  `game_name`,\n  `game_id`,\n  `discord_id`,\n  `role`\n)"
      ],
      "listRule": null,
      "viewRule": null,
      "createRule": null,
      "updateRule": null,
      "deleteRule": null,
      "options": {
        "allowEmailAuth": false,
        "allowOAuth2Auth": true,
        "allowUsernameAuth": false,
        "exceptEmailDomains": null,
        "manageRule": null,
        "minPasswordLength": 0,
        "onlyEmailDomains": null,
        "onlyVerified": false,
        "requireEmail": false
      }
    }
  ];

  const collections = snapshot.map((item) => new Collection(item));

  return Dao(db).importCollections(collections, true, null);
}, (db) => {
  return null;
})
