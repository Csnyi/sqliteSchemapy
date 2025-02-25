import os
import argparse
from tabulate import tabulate
from model import Table
from database import Database

class Controller:
    def __init__(self, db_path, *args, **kwargs):
        self.db = Database(db_path)
        self.models = {table: Table(self.db, table) for table in self.db.fetch_tables()}
    
    def choice_table(self):
        table_name = input("Table name: ").strip()
        if table_name not in self.models:
            print(f"Table '{table_name}' not found!")
            return []
        else:
            table = self.models[table_name]
            return table
    
    def list_table(self):
        print(self.db.get_tables())
        
    def list_table_rows(self, table):
        header = list(table.columns.keys())
        rows = table.fetch_all()
        print(tabulate([header] + [list(row) for row in rows], headers="firstrow"))
    
    def add_row(self, table):
        params = {col: input(f"{col}: ").strip() for col in table.required_columns}
        table.set_required_data(**params)
        table.save()
        print(f"Added: {params}")
    
    def update_by_id(self, table):
        row_id = input("Row ID: ").strip()
        if not row_id.isdigit():
            print("Invalid ID!")
        else:
            row = table.fetch_one_by_id(int(row_id))
            if row:
                params = {col: input(f"{col}: ").strip() for col in input("Columns (comma-separated): ").split(", ") if col in table.columns}
                if params:
                    table.set_data(id=int(row_id), **params)
                    table.save()
                    print(f"Updated: {params}")
                else:
                    print("Invalid column!")
            else:
                print("Invalid ID!")

    def update_customize(self, table):
        where_clauses = input("Where clause: ").strip()
        is_column = []
        where_columns = []
        if "and" in where_clauses:
            where_clause = where_clauses.split(" and ")
            for clause in where_clause:
                where_columns.append(clause.split("=")[0].strip())
        else:
            where_columns.append(where_clauses.split("=")[0])
        for col in where_columns:
            if col in table.columns:
                is_column.append(col)
        if is_column:
            params = {col: input(f"{col}: ").strip() for col in input("Columns (comma-separated): ").split(", ") if col in table.columns}
            if params:
                try:
                    table.update_customize(where_clauses, **params)
                    print(f"Updated: {params}")
                except Exception as e:
                    print(f"Error {e}")
            else:
                print("Invalid column!")
        else:
            print("Invalid where clause!")
    
    def delete_row(self, table):
        row_id = input("Row ID: ").strip()
        if not row_id.isdigit():
            print("Invalid ID!")
        else:
            deleted = table.fetch_one_by_id(int(row_id))
            if deleted:
                table.delete(int(row_id))
                print(f"Deleted: {dict(zip(table.columns.keys(), deleted))}")
            else:
                print("Invalid ID!")
    
    def add_column(self, table):
        column_definition = input("Column definition: ")
        table.add_column(column_definition)
        print(f"Column added: {column_definition}")
     
    def execute_query(self):
        query = input("Query: ").strip()
        try:
            self.db.cursor.execute(query)  # Lekérdezés végrehajtása
            result = self.db.cursor.fetchall()  # Ha van visszatérő adat, ezt használjuk

            if result:  # Csak ha van eredmény, tabuláljuk ki
                headers = [desc[0] for desc in self.db.cursor.description] if self.db.cursor.description else []
                print(tabulate(result, headers=headers))
            else:
                print("Query executed successfully.")

            self.db.conn.commit()  # Módosító parancsok után commit szükséges!
            
        except Exception as e:
            print(f"Query error: {e}")
                
    def quit(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("\nGoodbye!")
        self.db.close()

