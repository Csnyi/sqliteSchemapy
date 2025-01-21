BEGIN TRANSACTION;
CREATE TABLE "accounts" (
	"id"	INTEGER,
	"account_number"	INTEGER,
	"balance"	REAL NOT NULL,
	"interest_rate"	REAL DEFAULT 0.0,
	"user_id"	INTEGER,
	"timestamp"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "accounts" VALUES(1,1002,3400.0,0.03,1,'2025-01-13 06:28:13');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('accounts',1);
INSERT INTO "sqlite_sequence" VALUES('users',3);
CREATE TABLE "users" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"timestamp"	DATETIME DEFAULT CURRENT_TIMESTAMP, 'valid' BOOLEAN DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "users" VALUES(1,'Pool','2025-01-12 23:21:21',1);
INSERT INTO "users" VALUES(3,'Laki','2025-01-13 07:03:28',1);
COMMIT;
