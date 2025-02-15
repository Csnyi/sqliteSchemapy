# database_migrate.py 
import os
import textwrap
from templates.models.database.database import Database 
from migration.dir_structure import *
from migration.model_file_migrate import *
from migration.tables_controller_migrate import *
from migration.cli_view_migrate import *
from migration.db_main_migrate import *

def main(app_root, db_file_path, models_tables, tables_controller, cli_view, db_main, dump_file):
    app_root_len = len(app_root)+1
    db = Database(db_file_path)
    # table info: (id, name, type, notnull, default_value, pk)
    table_info = db.get_table_info()

    for table, columns in table_info.items():
        model_file_migrate(textwrap, table, columns, models_tables)

    tables_controller_migrate(app_root_len, table_info, os, models_tables, tables_controller)

    cli_view_migrate(textwrap, table_info, cli_view)

    db_main_migrate(cli_view, tables_controller, app_root_len, table_info, textwrap, db_main)

    db.backup(dump_file)

    db.close()
    print("Migration is complete!")

if __name__ == '__main__':
    config = load_config()
    
    # create directories and files
    create_folders(config["migrate"]["Paths"])
    create_files(config["migrate"]["Files"])
    # copy processes only the [CopyFiles] section
    if "CopyFiles" in config["migrate"]:
        copy_static_files(config["migrate"]["CopyFiles"])

    params = {
        "app_root": config["kwargs"]["app_root"],
        "db_file_path": config["kwargs"]["db_file_path"],
        "models_tables": config["kwargs"]["models_tables"],
        "tables_controller": config["kwargs"]["tables_controller"],
        "cli_view": config["kwargs"]["cli_view"],
        "db_main": config["kwargs"]["db_main"],
        "dump_file": config["kwargs"]["dump_file"]
    }

    main(**params)
