BEGIN TRANSACTION;
DROP TABLE IF EXISTS "offers";
CREATE TABLE IF NOT EXISTS "offers" (
	"id"	INTEGER NOT NULL UNIQUE,
	"user_id"	INTEGER NOT NULL,
	"name"	TEXT,
	"description"	TEXT,
	"marker_latitude"	REAL,
	"marker_longitude"	REAL,
	"is_complete"	INTEGER NOT NULL DEFAULT 0,
	"is_ready"	INTEGER DEFAULT 0,
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
DROP TRIGGER IF EXISTS "check_offer_ready";
CREATE TRIGGER check_offer_ready
   AFTER UPDATE 
   ON offers
BEGIN
	UPDATE offers
	SET is_ready = 1
	WHERE name NOTNULL
	AND description NOTNULL;
END;
DROP TRIGGER IF EXISTS "check_offer_complete";
CREATE TRIGGER check_offer_complete
   AFTER UPDATE 
   ON offers
BEGIN
	UPDATE offers
	SET is_complete = 1
	WHERE name NOTNULL
	AND description NOTNULL
	AND marker_latitude NOTNULL
	AND marker_longitude NOTNULL;
END;
COMMIT;
