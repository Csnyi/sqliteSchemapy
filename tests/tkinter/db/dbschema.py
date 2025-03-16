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

    def executemany(self, query, params_list):
        self.cursor.executemany(query, params_list)
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
        return [', '.join([*row]) for row in self.fetchall(query)]

    def backup(self, file_path):
        with open(file_path, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

    def restore(self, file_path):
        with open(file_path, "r") as f:
            sql_script = f.read()
            self.conn.executescript(sql_script)

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

    def insertmany(self, rows):
        """Új sorokat szúr be tömbösített formában."""
        if not rows:
            return  # Ha üres a bemenet, nincs teendő

        columns = ', '.join(rows[0].keys())  # Az első elem kulcsai alapján az oszlopok
        placeholders = ', '.join(['?'] * len(rows[0]))
        values = [tuple(row.values()) for row in rows]  # Több soros lista

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.db.executemany(query, values)
    
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

    def empty(self):
        self.db.cursor.execute('PRAGMA foreign_keys = OFF;')
        query = f"DELETE FROM {self.table_name}"
        self.db.execute(query)
        query_seq = 'DELETE FROM "sqlite_sequence"'
        self.db.execute(query_seq)
    
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

    def exec_custom(self):
        query = input("Query: ")
        self.db.execute(query)

def fetch_all(table):
    return [dict(row) for row in table.fetch_all()]

def fetch_one_by_id(table, row_id):
    return dict(table.fetch_one_by_id(row_id))

def list_table(db):
    print(db.get_tables())

def list_data(table_class):
    try:
        rows = table_class.fetch_all()
        header = [col for col in table_class.columns]
        table = [header]
        tablerows = [row for row in rows]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))
    except Exception as e:
        print(e)

def add_data(table, params):
    table.set_required_data(**params)
    table.save()
    print("Inserted:", table.id, params)

def add_many(table, params_list):
    """Több soros beszúrás dinamikusan."""
    if not params_list:
        return

    # Szűrés csak az oszlopnevekre
    clean_data = [
        {k: v for k, v in row.items() if k in table.columns} for row in params_list
    ]
    table.insertmany(clean_data)
    print("Inserted:", clean_data)

def update_data(table, row_id, params):
    params["id"] = row_id
    table.set_data(**params)
    table.save()
    print("Updated:", params)

def delete_row(table, row_id):
    table.delete(row_id)
    print(f"Deleted row {row_id}")
    list_data(table)

def empty_table(table):
    table.empty()
    print(f"Deleted {table.table_name}")

def show_columns(table):
    print("All columns:", table.columns)

def show_required_columns(table):
    print("Required columns:", table.required_columns)

def add_column(table):
    column_definition = input("Column definition: ")
    table.add_column(column_definition)
    print(f"Added column: {column_definition}")
    
def exec_custom(table):
    table.exec_custom()
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Database CLI")

    parser.add_argument("db", help="Database path")
    parser.add_argument("command", choices=["dblist", "list", "add", "upd", "del", "cols", "req_cols", "add_col", "exec"], help="Command to execute")
    parser.add_argument("table", help="Table name")
    parser.add_argument("--id", type=int, help="Row ID (for update/delete)")
    parser.add_argument("--data", nargs="*", help="Key=Value pairs for add/update")

    args = parser.parse_args()
    db = Database(args.db)

    if args.table in db.fetch_tables():
        table = Table(db, args.table)
    else:
        print(f"'{args.table}' invalid table!")

    if args.command == "dblist":
        list_table(db)
    
    elif args.command == "list":
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
            delete_row(table, args.id)

    elif args.command == "cols":
        show_columns(table)

    elif args.command == "req_cols":
        show_required_columns(table)
    
    elif args.command == "add_col":
        add_column(table)
        
    elif args.command == "exec":
        exec_custom(table)
        
