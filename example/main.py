# main.py example
import argparse
import configparser
from validation.validator import Validator
from models.database.database import Database
from views.cli_view import CLIView
from controllers.tables_controller import TablesController
from controllers.generate_deleter import GenerateDeleter

def main(db_file):
    db = Database(db_file)
    controller = TablesController(db)
    view = CLIView()
    valid = Validator(db)
    deleter = GenerateDeleter(db)

    # The more functions...
    # For example:
    while True:
        view.display_menu()
        choice = input("Option: ")

        if choice == "cls":
            view.cls()

        elif choice == "empty":
            table = input("Table name: ")
            controller.empty_table(table)
            print("Emptied table!")

        elif choice == "dfk":
            try:
                dfk = controller.check_foreign_key()
                print(dfk)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "fka":
            print(valid.get_foreign_key_list_all())
            
        elif choice == "sql":
            try:
                sql = db.get_sql()
                table = input("Table name: ")
                if table not in sql:
                    raise Exception("Table not found!")
                print(sql[table])
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "accol":
            try:
                controller.get_list("accounts")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "aacco":
            try:
                message = controller.add_data("accounts")
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "uacco":
            try:
                message = controller.add_data("accounts", True)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "dacco":
            try:
                id = int(input("Account id: "))
                message = deleter.delete_data("accounts", id)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "userl":
            try:
                controller.get_list("users")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "auser":
            try:
                message = controller.add_data("users")
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "uuser":
            try:
                message = controller.add_data("accounts", True)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "duser":
            try:
                id = input("User id: ")
                message = controller.delete_data("users", id)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "q":
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

