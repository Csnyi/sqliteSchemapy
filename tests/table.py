import sqlite3

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

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

class Table:
    def __init__(self, db: Database, table_name: str):
        self.db = db
        self.table_name = table_name
        self.columns = self._get_table_info()

    def _get_table_info(self):
        """Lekérdezi az oszlopokat és azok típusait egy dict-ben tárolva."""
        query = f"PRAGMA table_info({self.table_name})"
        return {row[1]: row[2] for row in self.db.fetchall(query)}

    def fetch_all(self):
        """Visszaadja az összes sort a táblából."""
        query = f"SELECT * FROM {self.table_name}"
        return self.db.fetchall(query)

    def fetch_one_by_id(self, row_id):
        """Visszaad egy sort az ID alapján."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.db.fetchone(query, (row_id,))

    def insert(self, **kwargs):
        """Új sort szúr be dinamikusan az oszlopok alapján."""
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = tuple(kwargs.values())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        return self.db.lastrowid(query, values)

    def update(self, row_id, **kwargs):
        """Frissít egy sort az ID alapján."""
        set_clause = ', '.join([f"{col} = ?" for col in kwargs.keys()])
        values = tuple(kwargs.values()) + (row_id,)
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        self.db.execute(query, values)

    def delete(self, row_id):
        """Töröl egy sort az ID alapján."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self.db.execute(query, (row_id,))

class Users(Table):
    def __init__(self, db: Database):
        super().__init__(db, "users")
        for col in self.columns:
            setattr(self, col, None)

    def set_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.columns:
                setattr(self, key, value)

    def save(self):
        if hasattr(self, "id") and self.id:
            current_data = self.fetch_one_by_id(self.id)  # Meglévő adatok lekérése
            if current_data:
                existing_values = dict(zip(self.columns.keys(), current_data))
                update_data = {k: v for k, v in self.__dict__.items()
                            if k in self.columns and k != "id" and v is not None and v != existing_values.get(k)}
                if update_data:  # Csak ha van tényleges változás
                    self.update(self.id, **update_data)
        else:
            self.id = self.insert(**{k: v for k, v in self.__dict__.items() if k in self.columns})

class Accounts(Table):
    def __init__(self, db: Database):
        super().__init__(db, "accounts")
        for col in self.columns:
            setattr(self, col, None)

    def set_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.columns:
                setattr(self, key, value)

    def save(self):
        if hasattr(self, "id") and self.id:
            current_data = self.fetch_one_by_id(self.id)  # Meglévő adatok lekérése
            if current_data:
                existing_values = dict(zip(self.columns.keys(), current_data))
                update_data = {k: v for k, v in self.__dict__.items()
                            if k in self.columns and k != "id" and v is not None and v != existing_values.get(k)}
                if update_data:  # Csak ha van tényleges változás
                    self.update(self.id, **update_data)
        else:
            self.id = self.insert(**{k: v for k, v in self.__dict__.items() if k in self.columns})


# Példa használat
if __name__ == "__main__":
    db = Database("db/bank.db")
    accounts = Accounts(db)
    accounts.set_data(id=3, account_number=1007373000971070, balance=50000)
    accounts.save()
    print("All accounts:", accounts.fetch_all())
    db.close()
