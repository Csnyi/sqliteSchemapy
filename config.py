import os
import argparse
import configparser
from configparser import ConfigParser, ExtendedInterpolation

def load_config():
    parser = argparse.ArgumentParser(description="SQLite Model Generator.")
    parser.add_argument("--app_root", type=str, help="Az app elérési útja.")
    parser.add_argument("--db_file_path", type=str, help="Az adatbázis fájl elérési útja.")
    parser.add_argument("--models_tables", type=str, help="A modells/tables mappa elérési útja.")
    parser.add_argument("--tables_controller", type=str, help="A controller fájl elérési útja.")
    parser.add_argument("--cli_view", type=str, help="A view fájl elérési útja.")
    parser.add_argument("--db_main", type=str, help="A main fájl elérési útja.")
    parser.add_argument("--dump_file", type=str, help="A dump fájl elérési útja.")
    parser.add_argument("--config", type=str, default="config.ini", help="A konfigurációs fájl elérési útja.")
    
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="Listázza az adatbázis tábláit")
    subparsers.add_parser("generate", help="Generálja az appot az adatbázishoz")
    subparsers.add_parser("runcli", help="Futtatja a CLI-t az adatbázishoz")

    args = parser.parse_args()

    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(os.path.join(os.path.dirname(__file__), args.config))

    # Dict to make directories
    CONFIG_VALUES = {section: dict(config.items(section)) for section in config.sections()}

    # kwargs to migration
    kwargs = {
        "app_root": args.app_root or config["Paths"].get("app_root", ""),
        "db_file_path": args.db_file_path or config["DbFile"].get("db_file_path", ""),
        "models_tables": args.models_tables or config["Paths"].get("models_tables", ""),
        "tables_controller": args.tables_controller or config["Files"].get("tables_controller", ""),
        "cli_view": args.cli_view or config["Files"].get("cli_view", ""),
        "db_main": args.db_main or config["Files"].get("db_main", ""),
        "dump_file": args.dump_file or config["Files"].get("dump_file", "")
    }

    return {"parser": parser, "args": args, "kwargs": kwargs, "migrate": CONFIG_VALUES}
