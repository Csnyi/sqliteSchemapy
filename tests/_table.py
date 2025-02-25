import sqlite3
import os
import platform
import argparse
from tabulate import tabulate

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

class Table:
    def __init__(self, db: Database, table_name: str):
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
                self.id = self.insert(**{k: v for k, v in self.__dict__.items() if k in self.required_columns})
        except Exception as e:
            raise Exception(f"Save error: {e}")

    def add_column(self, column_definition):
        query = f"ALTER TABLE {self.table_name} ADD COLUMN {column_definition}"
        self.db.execute(query)

def create_models(database):
    db = database
    tables = db.fetch_tables()

    models = {}
    for table in tables:
        columns = db.fetch_columns(table)
        attrs = {col: None for col in columns}  # Alapértelmezett attribútumok
        models[table] = type(table.capitalize(), (Table,), attrs)

    return models

def main():
    db = Database("../db/bank.db")
    models = {table: Table(db, table) for table in db.fetch_tables()}  # Előre létrehozott példányok

    options = '''
    Options: 
    dblist  - List table names
    list    - List table rows
    add     - Add data
    upd     - Update data
    del     - Delete data
    cols    - Show table columns
    req_cols - Show required columns
    add_col - Add column to table
    ex      - Execute custom query
    q       - Quit
    '''

    while True:
        print(options)
        choice = input("Option: ").strip().lower()

        if choice == "dblist":
            print(db.get_tables())

        elif choice in {"list", "add", "upd", "del", "cols", "req_cols", "add_col"}:
            table_name = input("Table name: ").strip()
            if table_name not in models:
                print(f"Table '{table_name}' not found!")
                continue
            
            table = models[table_name]

            if choice == "list":
                header = list(table.columns.keys())
                rows = table.fetch_all()
                print(tabulate([header] + [list(row) for row in rows], headers="firstrow"))

            elif choice == "add":
                params = {col: input(f"{col}: ").strip() for col in table.required_columns}
                table.set_required_data(**params)
                table.save()
                print(f"Added: {params}")

            elif choice == "upd":
                row_id = input("Row ID: ").strip()
                if not row_id.isdigit():
                    print("Invalid ID!")
                    continue
                
                params = {col: input(f"{col}: ").strip() for col in input("Columns (comma-separated): ").split(", ")}
                table.set_data(id=int(row_id), **params)
                table.save()
                print(f"Updated: {params}")

            elif choice == "del":
                row_id = input("Row ID: ").strip()
                if not row_id.isdigit():
                    print("Invalid ID!")
                    continue
                
                deleted = table.fetch_one_by_id(int(row_id))
                if deleted:
                    table.delete(int(row_id))
                    print(f"Deleted: {dict(zip(table.columns.keys(), deleted))}")
                else:
                    print("Row not found!")

            elif choice == "cols":
                print(f"{table_name} columns: {list(table.columns.keys())}")

            elif choice == "req_cols":
                print(f"{table_name} required columns: {list(table.required_columns.keys())}")

            elif choice == "add_col":
                column_definition = input("Column definition: ")
                table.add_column(column_definition)
                print(f"Column added: {column_definition}")

        elif choice == "ex":
            query = input("Query: ").strip()
            try:
                db.cursor.execute(query)  # Lekérdezés végrehajtása
                result = db.cursor.fetchall()  # Ha van visszatérő adat, ezt használjuk
                
                if result:  # Csak ha van eredmény, tabuláljuk ki
                    headers = [desc[0] for desc in db.cursor.description] if db.cursor.description else []
                    print(tabulate(result, headers=headers))
                else:
                    print("Query executed successfully.")
                
                db.conn.commit()  # Módosító parancsok után commit szükséges!
            
            except sqlite3.Error as e:
                print(f"Query error: {e}")

        elif choice == "q":
            os.system("cls" if os.name == "nt" else "clear")
            print("\nGoodbye!")
            db.close()
            break

        else:
            print(f"Invalid option: {choice}")

if __name__ == "__main__":
    
    main()