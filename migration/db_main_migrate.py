# migrate -> /db_main.py

def db_main_migrate(cli_view, tables_controller, app_root_len, table_info, textwrap, db_main):

    from_view = cli_view.replace('/', '.')[app_root_len:-3]
    from_controllers = "" 
    
    elif_list = ""
    for table_name in table_info:
        class_name = table_name.capitalize()
        option = table_name[:4]
        elif_list += textwrap.dedent(f'''\
            elif choice == "{option}l":
                {"":>20}try:
                    {"":>20}controller.get_list("{table_name}")
                {"":>20}except Exception as error:
                    {"":>20}print(f"\\n{{str(error)}}")
                    
        ''')
        elif_list += f'''{"":>20}'''

    with open(db_main, 'w') as f:
        content = textwrap.dedent(f'''\
            # {db_main}
            import os
            import argparse
            import configparser
            from configparser import ConfigParser, ExtendedInterpolation
            from models.database.database import Database
            from {from_view} import CLIView
            from controllers.database.db_controller import DbController

            def main(db_file):
                db = Database(db_file)
                controller = DbController(db)
                view = CLIView()
            
                # The more functions...
                # For example:
                while True:
                    view.display_menu()
                    choice = input("Option: ")

                    if choice == "cls":
                        view.cls()
        
                    elif choice == "add":
                        try:
                            table = input("Table name: ")
                            controller.add_data(table)
                        except Exception as e:
                            print(e)
                    
                    elif choice == "up":
                        try:
                            table_name = input("Table: ")
                            cols = input("Cols: ").split(", ")
                            state = input("State: ")
                            params = input("Params: ").split(", ")
                            controller.update(table_name, cols, state, params)
                        except Exception as e:
                            print(e) 
                    
                    elif choice == "del":
                        try:
                            table = input("Table name: ")
                            row_id = input("Row ID: ")
                            controller.delete(table, row_id)
                            print(f"Row {{row_id}} deleted in {{table}}")
                        except Exception as e:
                            print(e) 
                    
                    elif choice == "delall":
                        try:
                            table = input("Table name: ")
                            row_id = input("Row ID: ")
                            controller.delete_data(table, row_id)
                            print(f"Row {{row_id}} deleted in {{table}}")
                        except Exception as e:
                            print(e) 
                            
                    elif choice == "empty":
                        table = input("Table name: ")
                        controller.empty_table(table)
                        print("Emptied table!")
                    
                    {elif_list}
                    elif choice == "q":
                        db.close()
                        view.cls()
                        print("Goodby!")
                        break 
            
            if __name__ == '__main__':
                parser = argparse.ArgumentParser(description="Main script.")
                parser.add_argument("--db_file", type=str, help="Az adatbázis fájl elérési útja.")
                parser.add_argument("--config", type=str, default="../config.ini", help="A konfigurációs fájl elérési útja.")
                args = parser.parse_args()
                config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
                config.read(os.path.join(os.path.dirname(__file__), args.config))
                db_file = args.db_file or config["DbFile"]["db_file_path"]
                main(db_file)

        ''')
        f.write(content)
