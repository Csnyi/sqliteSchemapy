import sqlite3

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row 
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON;')

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def lastrowid(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.conn.close()

    def fetch_tables(self):
        """Lekérdezi az adatbázis tábláit"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row["name"] for row in self.cursor.fetchall()]

    def fetch_columns(self, table_name):
        """Lekérdezi egy adott tábla oszlopait"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row["name"] for row in self.cursor.fetchall()]

    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' and tbl_name != 'sqlite_sequence';"
        return [row[0] for row in self.fetchall(query)]
