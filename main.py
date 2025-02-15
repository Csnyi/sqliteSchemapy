# main.py
import database_migrate as dm
import subprocess
import sys

def list_tables(db_file_path):
    db = dm.Database(db_file_path)
    tables = [table for table in db.get_table_info()]
    print("Tables: ", ", ".join(tables))

def create_app(config):
    # create directories and files
    dm.create_folders(config["migrate"]["Paths"])
    dm.create_files(config["migrate"]["Files"])
    # copy processes only the [CopyFiles] section
    if "CopyFiles" in config["migrate"]:
        dm.copy_static_files(config["migrate"]["CopyFiles"])

    params = {
        "app_root": config["kwargs"]["app_root"],
        "db_file_path": config["kwargs"]["db_file_path"],
        "models_tables": config["kwargs"]["models_tables"],
        "tables_controller": config["kwargs"]["tables_controller"],
        "cli_view": config["kwargs"]["cli_view"],
        "db_main": config["kwargs"]["db_main"],
        "dump_file": config["kwargs"]["dump_file"]
    }

    dm.main(**params)

def run_cli(config):
    db_main = config["kwargs"]["db_main"]
    subprocess.run([sys.executable, db_main])

def main():
    config = dm.load_config()

    if config["args"].command == "list":
        db = config["kwargs"]["db_file_path"]
        list_tables(db)
    elif config["args"].command == "generate":
        create_app(config)
    elif config["args"].command == "runcli":
        run_cli(config)
    else:
        config["parser"].print_help()

if __name__ == "__main__":
    main()

