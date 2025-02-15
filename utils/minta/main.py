# main.py example
import argparse
import configparser
from validation.validator import Validator
from validation.translate import *
from models.database.database import Database
from views.actions import actions
from views.cli_view import CLIView
from controllers.tables_controller import TablesController
from controllers.generate_deleter import GenerateDeleter

def main(db_file):
    db = Database(db_file)
    controller = TablesController(db)
    view = CLIView()
    valid = Validator(db)
    deleter = GenerateDeleter(db)

    try:
        actions(db_file, db, controller, view, valid, deleter)
    except Exception as e:
        print(f"Action error: {e}")

if __name__ == '__main__':
    # Argumentumok beolvasása
    parser = argparse.ArgumentParser(description="Main script.")
    parser.add_argument("--db_file", type=str, help="Az adatbázis fájl elérési útja.")
    parser.add_argument("--config", type=str, default="config.ini", help="A konfigurációs fájl elérési útja.")

    args = parser.parse_args()

    # Konfigurációs fájl beolvasása
    config = configparser.ConfigParser()
    config.read(args.config)

    # Argumentumok vagy konfigurációs fájl használata
    db_file = args.db_file or config["Paths"]["db_file"]

    main(db_file)

