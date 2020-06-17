BEGIN TRANSACTION;
DROP TABLE IF EXISTS "offers";
CREATE TABLE IF NOT EXISTS "offers" (
	"id"	INTEGER NOT NULL UNIQUE,
	"user_id"	INTEGER,
	"name"	TEXT,
	"description"	TEXT,
	"marker_latitude"	REAL,
	"marker_longitude"	REAL,
	"is_complete"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
DROP TABLE IF EXISTS "users";
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT,
	"phone"	TEXT,
	PRIMARY KEY("id")
);
COMMIT;
