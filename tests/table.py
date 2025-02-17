import sqlite3
import os
import platform
from tabulate import tabulate

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
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

class Table:
    def __init__(self, db: Database, table_name: str):
        self.db = db
        self.table_name = table_name
        self.columns = self._get_table_info()
        self.required_columns = self.get_required_columns()

    def get_required_columns(self):
        """Lekérdezi az ajánlott oszlopokat és azok típusait egy dict-ben tárolva."""
        query = f"PRAGMA table_info({self.table_name})"
        return {row[1]: row[2] for row in self.db.fetchall(query) if row[4] is None and row[5] == 0}

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

class Users(Table):
    def __init__(self, db: Database):
        super().__init__(db, "users")
        for col in self.columns:
            setattr(self, col, None)

class Accounts(Table):
    def __init__(self, db: Database):
        super().__init__(db, "accounts")
        for col in self.columns:
            setattr(self, col, None)

class Address(Table):
    def __init__(self, db: Database):
        super().__init__(db, "address")
        for col in self.columns:
            setattr(self, col, None)

@staticmethod
def cls():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# Példa használat
if __name__ == "__main__":
    db = Database("../db/bank.db")
    
    while True:
        choice = input("Option: ")
        
        if choice == "list":
            try:
                table_name = input("Table name: ")
                class_name = table_name.capitalize()
                table_class = globals().get(class_name)(db)
                rows = table_class.fetch_all()
                header = [col for col in table_class.columns]
                table = [header]
                tablerows = [row for row in rows]
                table.extend(tablerows)
                print(tabulate(table, headers="firstrow"))
            except Exception as e:
                print(e)

        if choice == "add":
            try:
                table_name = input("Table name: ")
                class_name = table_name.capitalize()
                table = globals().get(class_name)(db)
                cols = table.required_columns
                params = {}
                for col in cols:
                    params[col] = input(f"{col}: ")
                table.set_required_data(**params)
                table.save()
                print(f"{params} Data added to {table_name}")
            except Exception as e:
                print(e)
        
        elif choice == "upd":
            try:
                table_name = input("Table name: ")
                class_name = table_name.capitalize()
                table = globals().get(class_name)(db)
                params = {}
                params["id"] = int(input("id: "))
                cols = input("columns: ").split(", ")
                for col in cols:
                    params[col] = input(f"{col}: ")
                table.set_data(**params)
                table.save()
                print(f"{params} Data updated to {table_name}")
            except Exception as e:
                print(e)

        elif choice == "del":
            try:
                table_name = input("Table name: ")
                class_name = table_name.capitalize()
                table = globals().get(class_name)(db)
                id = int(input("Row ID: "))
                deleted = table.fetch_one_by_id(id)
                table.delete(id)
                print(f"{deleted} Data deleted to {table_name}")
            except Exception as e:
                print(e)

        elif choice == "cols":
            table_name = input("Table name: ")
            class_name = table_name.capitalize()
            table = globals().get(class_name)(db)
            print(f"{table_name} columns: {[col for col in table.columns]}")

        elif choice == "req_cols":
            table_name = input("Table name: ")
            class_name = table_name.capitalize()
            table = globals().get(class_name)(db)
            print(f"{table_name} required columns: {table.required_columns}")
        
        elif choice == "q":
            cls()
            print(f"\nGoodby!")
            break
            db.close()
    
'''
import argparse

def list_data(table):
    print(table.fetch_all())

def add_data(table, params):
    table.set_data(**params)
    table.save()
    print("Inserted:", table.fetch_all())

def update_data(table, row_id, params):
    params["id"] = row_id
    table.set_data(**params)
    table.save()
    print("Updated:", table.fetch_all())

def delete_data(table, row_id):
    table.delete(row_id)
    print(f"Deleted row {row_id}")

def show_columns(table):
    print("All columns:", table.get_all_columns())

def show_required_columns(table):
    print("Required columns:", table.columns)

if __name__ == "__main__":
    db = Database("../db/bank.db")

    parser = argparse.ArgumentParser(description="Database CLI")

    parser.add_argument("command", choices=["list", "add", "upd", "del", "cols", "req_cols"], help="Command to execute")
    parser.add_argument("table", help="Table name")
    parser.add_argument("--id", type=int, help="Row ID (for update/delete)")
    parser.add_argument("--data", nargs="*", help="Key=Value pairs for add/update")

    args = parser.parse_args()

    class_name = args.table.capitalize()
    table = globals().get(class_name)(db)

    if args.command == "list":
        list_data(table)

    elif args.command == "add":
        if not args.data:
            print("No data provided!")
        else:
            params = {k: v for k, v in (item.split("=") for item in args.data)}
            add_data(table, params)

    elif args.command == "upd":
        if not args.id or not args.data:
            print("Update requires --id and --data!")
        else:
            params = {k: v for k, v in (item.split("=") for item in args.data)}
            update_data(table, args.id, params)

    elif args.command == "del":
        if not args.id:
            print("Delete requires --id!")
        else:
            delete_data(table, args.id)

    elif args.command == "cols":
        show_columns(table)

    elif args.command == "req_cols":
        show_required_columns(table)
'''