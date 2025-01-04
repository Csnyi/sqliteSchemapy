import argparse
import configparser
import textwrap
from models.database.database import Database

def main(db_file, info_file, model_path, controller_file, view_file, main_file, dump_file):
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
        model_file = f'{model_path}{table}.py'
        attributes = tuple(col['name'] for col in columns)
        init_args = ', '.join([f"{arg}=None" for arg in attributes])
        init_body = '\n                        '.join(f"self.{arg} = {arg}" for arg in attributes)
        attrs = ", ".join([f"{attr}={{self.{attr}!r}}" for attr in attributes])
        fetch_col = ', '.join([f"{col}" for col in attributes])
        update_set = ", ".join([f"{attr} = ?" for attr in attributes if attr != 'id'])
        update_param = ", ".join([f"self.{attr}" for attr in attributes if attr != 'id'])
        insert_set = ", ".join(attributes)
        insert_val = ", ".join(["?" for _ in attributes])
        insert_param = ", ".join([f"self.{attr}" for attr in attributes])
        
        with open(model_file, 'w') as f:
            content = textwrap.dedent(f'''\
                #{model_file}
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

    from_info = info_file.replace('/', '.')[:-3]
    path = model_path.replace('/', '.')
    from_model = '\n            '.join(f"from {path}{table} import {table.capitalize()}" for table in table_info)
    table_names = [*(table for table in table_info)]
    list_functions = ""
    elif_list = ""
    display_menu = textwrap.dedent(f'''\
        print(f\'\'\'
        {"":>16}Options:
    ''')
    for table_name in table_names:
        class_name = table_name.capitalize()
        list_functions += textwrap.dedent(f'''\
            def {table_name}_list(self):
                {"":>16}{table_name} = {class_name}.fetch_all(self.db)
                {"":>16}header = [*(colname for colname in self.info.table_colnames["{table_name}"])]
                {"":>16}table = [header]
                {"":>16}tablerows = [[getattr(col, attr) for attr in header] for col in {table_name}]
                {"":>16}table.extend(tablerows)
                {"":>16}print(tabulate(table, headers="firstrow"))

        ''')
        list_functions += f'''{"":>16}'''
        option = table_name[:3]
        elif_list += textwrap.dedent(f'''\
            elif ch == "{option}l":
                {"":>20}controller.{table_name}_list()
        ''')
        elif_list += f'''{"":>20}'''
        display_menu += f'''\
            {"":>8}{option}l:\\t{class_name} List\n'''

    display_menu += f'''\
        {"":>12}cls:\\tClear Screen
        {"":>12}q:\\tQuit
        {"":>8}\'\'\')'''

    with open(controller_file, 'w') as f:
        content = textwrap.dedent(f'''\
            # {controller_file}
            import datetime
            from tabulate import tabulate
            from {from_info} import Info
            {from_model}
            
            class TablesController:
                def __init__(self, db):
                    self.db = db
                    self.info = Info()

                {list_functions}
                
        ''')
        f.write(content)

    with open(view_file, 'w') as f:
        content = textwrap.dedent(f'''\
            # {view_file}
            import os
            import platform

            class CLIView:
                @staticmethod
                def display_menu():
                    {display_menu}

                @staticmethod
                def get_user_input(prompt):
                    return input(prompt)

                @staticmethod
                def display_message(message):
                    print(message)

                @staticmethod
                def cls():
                    if platform.system() == "Windows":
                        os.system("cls")
                    else:
                        os.system("clear")
        ''')
        f.write(content)

    from_view = view_file.replace('/', '.')[:-3]
    from_controllers = controller_file.replace('/', '.')[:-3]

    with open(main_file, 'w') as f:
        content = textwrap.dedent(f'''\
            # {main_file}
            import argparse
            import configparser
            from models.database.database import Database
            from {from_view} import CLIView
            from {from_controllers} import TablesController

            def main(db_file):
                db = Database(db_file)
                controller = TablesController(db)
                view = CLIView()
            
                # The more functions...
                # For example:
                while True:
                    view.display_menu()
                    ch = input("Option: ")

                    if ch == "cls":
                        view.cls()

                    {elif_list}
                    elif ch == "q":
                        db.close()
                        view.cls()
                        print("Goodby!")
                        break 
            
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
    parser.add_argument("--model_path", type=str, help="A modellek mappa elérési útja.")
    parser.add_argument("--controller_file", type=str, help="A controller fájl elérési útja.")
    parser.add_argument("--view_file", type=str, help="A view fájl elérési útja.")
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
    model_path = args.model_path or config["Paths"]["model_path"]
    controller_file = args.controller_file or config["Paths"]["controller_file"]
    view_file = args.view_file or config["Paths"]["view_file"]
    main_file = args.main_file or config["Paths"]["main_file"]
    dump_file = args.dump_file or config["Paths"]["dump_file"]

    main(db_file, info_file, model_path, controller_file, view_file, main_file, dump_file)
