# main.py
import argparse
import configparser
from models.database.database import Database
from views.cli_view import CLIView
from controllers.tables_controller import TablesController

def main(db_file):
    db = Database(db_file)
    controller = TablesController(db)
    view = CLIView()

    # The more functions...
    # For example:
    while True:
        view.display_menu()
        choice = input("Option: ")

        if choice == "cls":
            view.cls()

        elif choice == "accol":
            try:
                controller.accounts_list()
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "cacco":
            try:
                controller.add_data_accounts()
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "userl":
            try:
                controller.users_list()
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "cuser":
            try:
                controller.add_data_users()
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

