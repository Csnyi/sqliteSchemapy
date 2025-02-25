
class Table:
    def __init__(self, db, table_name: str):
        self.db = db
        self.table_name = table_name
        self.columns = self.get_all_columns()
        self.required_columns = self.get_required_columns()
        for col in self.columns:
            setattr(self, col, None)
    
    def get_required_columns(self):
        """Lekérdezi az ajánlott oszlopokat és azok típusait egy dict-ben tárolva."""
        query = f"PRAGMA table_info({self.table_name})"
        return {row[1]: row[2] for row in self.db.fetchall(query) if row[4] is None and row[5] == 0}

    def get_all_columns(self):
        """Lekérdezi az oszlopokat és azok típusait egy dict-ben tárolva."""
        query = f"PRAGMA table_info({self.table_name})"
        return {row["name"]: row["type"] for row in self.db.fetchall(query)}
    
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

    def update_customize(self, where_clause, **kwargs):
        """Frissít egy sort az where clause alapján."""
        set_clause = ', '.join([f"{col} = ?" for col in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        self.db.execute(query, values)

    def delete(self, row_id):
        """Töröl egy sort az ID alapján."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self.db.execute(query, (row_id,))

    def set_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.columns:
                setattr(self, key, value)
    
    def set_required_data(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.required_columns:
                setattr(self, key, value)

    def save(self):
        try:
            if hasattr(self, "id") and self.id:
                current_data = self.fetch_one_by_id(self.id)  # Meglévő adatok lekérése
                if current_data:
                    existing_values = dict(zip(self.columns.keys(), current_data))
                    update_data = {k: v for k, v in self.__dict__.items()
                                if k in self.columns 
                                and k != "id" 
                                and v is not None 
                                and v != existing_values.get(k)}
                    if update_data:  # Csak ha van tényleges változás
                        self.update(self.id, **update_data)
            else:
                self.insert(**{k: v for k, v in self.__dict__.items() if k in self.required_columns})
        except Exception as e:
            raise Exception(f"Save error: {e}")

    def add_column(self, column_definition):
        query = f"ALTER TABLE {self.table_name} ADD COLUMN {column_definition}"
        self.db.execute(query)
