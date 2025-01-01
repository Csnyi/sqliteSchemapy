import argparse
import configparser
import textwrap
from models.database.database import Database

def main(db_file, info_file, model_file, controller_file, main_file, dump_file):
    db = Database(db_file)
    tabel_sql = db.get_sql()
    # table info: (id, name, type, notnull, default_value, pk)
    table_info = db.get_table_info()
    table_colnames = {table: tuple(col['name'] for col in columns) for table, columns in table_info.items()}
    
    with open(info_file, 'w') as f:
        content = textwrap.dedent(f"""\
            class Info: 
                def __init__(self):
                    self.table_colnames = dict()
                    self.table_info = dict()
                    self.table_sql = dict()

                    self.table_colnames = {table_colnames}
                    self.table_info = {table_info}
                    self.table_sql = {tabel_sql}
        """)
        f.write(content)

    for table, columns in table_info.items():
        class_name = table.capitalize()
        file = f'{model_file}{table}.py'
        attributes = table_colnames[table]
        init_args = ', '.join([f"{col}=None" for col in attributes])
        fetch_col = ', '.join([f"{col}" for col in attributes])
        init_body = '\n                        '.join(f"self.{col} = {col}" for col in attributes)
        attrs = ", ".join([f"{attr}={{self.{attr}!r}}" for attr in attributes])
        update_set = ", ".join([f"{attr} = ?" for attr in attributes if attr != 'id'])
        update_param = ", ".join([f"self.{attr}" for attr in attributes if attr != 'id'])
        insert_set = ", ".join(attributes)
        insert_val = ", ".join(["?" for _ in attributes])
        insert_param = ", ".join([f"self.{attr}" for attr in attributes])
        
        with open(file, 'w') as f:
            content = textwrap.dedent(f'''\
                #{file}
                class {class_name}:
                    def __init__(self, {init_args}):
                        {init_body}
                    
                    def __repr__(self):
                        return f"< {class_name}: ({attrs}) >"

                    @staticmethod
                    def fetch_all(db):
                        query = "SELECT {fetch_col} FROM {table}"
                        rows = db.fetchall(query)
                        return [{class_name}(*row) for row in rows]

                    @staticmethod
                    def fetch_one_by_id(db, id):
                        query = "SELECT {fetch_col} FROM {table} WHERE id = ?"
                        row = db.fetchone(query, (id,))
                        return {class_name}(*row) if row else None

                    def save(self, db):
                        if self.id: 
                            query = "UPDATE {table} SET {update_set} WHERE id = ?"
                            params = ({update_param}, self.id)
                        else: 
                            query = "INSERT INTO {table} ({insert_set}) VALUES ({insert_val})"
                            params = ({insert_param})
                        db.execute(query, params)

                    def delete(self, db):
                        if self.id:
                            query = "DELETE FROM {table} WHERE id = ?"
                            db.execute(query, (self.id,))

            ''')
            f.write(content)
    
    from_controller = ''
    for table in table_info:
        class_name = table.capitalize()
        path = model_file.replace('/', '.')
        from_controller += f'from {path}{table} import {class_name}\n'
    
    with open(controller_file, 'w') as f:
        content = textwrap.dedent(f'''\
# {controller_file}
import datetime
{from_controller}
class ModelController:
    def __init__(self, db):
        self.db = db
            
        ''')
        f.write(content)

    from_info = info_file.replace('/', '.')[:-3]
    from_main = controller_file.replace('/', '.')[:-3]

    with open(main_file, 'w') as f:
        content = textwrap.dedent(f'''\
# {main_file}
import argparse
import configparser
from models.database.database import Database
from {from_info} import Info
from {from_main} import ModelController

def main(db_file):
    db = Database(db_file)
    info = Info()
    controller = ModelController(db)
 
 # The more functions...
 
 if __name__ == '__main__':
    # Argumentumok beolvasása
    parser = argparse.ArgumentParser(description="Main script.")
    parser.add_argument("--db_file", type=str, help="Az adatbázis fájl elérési útja.")
    parser.add_argument("--config", type=str, default="config_migrate.ini", help="A konfigurációs fájl elérési útja.")

    args = parser.parse_args()

    # Konfigurációs fájl beolvasása
    config = configparser.ConfigParser()
    config.read(args.config)

    # Argumentumok vagy konfigurációs fájl használata
    db_file = args.db_file or config["Paths"]["db_file"]

    main(db_file)
 
        ''')
        f.write(content)

    db.iterdump(dump_file)
    db.close()
    print("Migration is complete!")

if __name__ == '__main__':
    # Argumentumok beolvasása
    parser = argparse.ArgumentParser(description="Database migration script.")
    parser.add_argument("--db_file", type=str, help="Az adatbázis fájl elérési útja.")
    parser.add_argument("--info_file", type=str, help="Az info fájl elérési útja.")
    parser.add_argument("--model_file", type=str, help="A modellek mappa elérési útja.")
    parser.add_argument("--controller_file", type=str, help="A controller fájl elérési útja.")
    parser.add_argument("--main_file", type=str, help="A main fájl elérési útja.")
    parser.add_argument("--dump_file", type=str, help="A dump fájl elérési útja.")
    parser.add_argument("--config", type=str, default="config_migrate.ini", help="A konfigurációs fájl elérési útja.")

    args = parser.parse_args()

    # Konfigurációs fájl beolvasása
    config = configparser.ConfigParser()
    config.read(args.config)

    # Argumentumok vagy konfigurációs fájl használata
    db_file = args.db_file or config["Paths"]["db_file"]
    info_file = args.info_file or config["Paths"]["info_file"]
    model_file = args.model_file or config["Paths"]["model_file"]
    controller_file = args.controller_file or config["Paths"]["controller_file"]
    main_file = args.main_file or config["Paths"]["main_file"]
    dump_file = args.dump_file or config["Paths"]["dump_file"]

    main(db_file, info_file, model_file, controller_file, main_file, dump_file)
