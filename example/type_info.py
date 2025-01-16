import argparse
import configparser
import textwrap
from models.database.database import Database

def main(db_file):
    db = Database(db_file)
    tabel_sql = db.get_sql()
    # table info: (id, name, type, notnull, default_value, pk)
    table_info = db.get_table_info()

    class Initialize:
        def __init__(self, table_info):
            self.table_info = table_info
            self.table_names = [table for table in table_info] 
            self.table_colnames = {table: tuple(col['name'] for col in columns) for table, columns in table_info.items()}
            
        def set_tables(self):
            return "valami beállítás"

        def validate_data(self, data):
            errors = {}
            for table_name in self.table_names:
                if table_name not in self.table_info:
                    return [f"Table '{table_name}' does not exist in the schema."]
                
                errors[table_name] = []

                schema = self.table_info[table_name]
                for column in schema:
                    col_name = column['name']
                    col_type = column['type']
                    notnull = column['notnull']
                    dflt_value = column['dflt_value']
                    pk = column['pk']

                    # Ellenőrizd, hogy az oszlop létezik-e az adatokban
                    if col_name not in data:
                        if notnull and dflt_value is None:
                            errors[table_name].append(f"Missing required field '{col_name}'.")
                        continue

                    value = data[col_name]

                    # Ellenőrizd, hogy az érték nem NULL, ha kötelező
                    if notnull and value is None:
                        errors[table_name].append(f"Field '{col_name}' cannot be NULL.")

                    # Ellenőrizd az adattípust (egyszerűsített példa)
                    if col_type.upper() == "INTEGER" and not isinstance(value, int):
                        errors[table_name].append(f"Field '{col_name}' must be an integer number.")
                    elif col_type.upper() == "REAL" and not isinstance(value, float):
                        errors[table_name].append(f"Field '{col_name}' must be a float number.")
                    elif col_type.upper() == "TEXT" and not isinstance(value, str):
                        errors[table_name].append(f"Field '{col_name}' must be a string.")
                    elif col_type.upper() == "BOOLEAN" and not isinstance(value, int):
                        errors[table_name].append(f"Field '{col_name}' must be a 1 or 0.")

                    # Elsődleges kulcs validáció (csak ha szükséges)
                    if pk and value is None:
                        errors[table_name].append(f"Primary key field '{col_name}' cannot be NULL.")

            return errors


    init_valid = Initialize(table_info)

    data = {
        "name": "Mazsi",
        "account_number": 1002,
        "balance": 2300.0,
        "interest_rate": 0.06
    }

    # Validáció
    errors = init_valid.validate_data(data)
    if any(errors.values()):
        for key, error in errors.items():
            if error:
                for er in error:
                    print(f"Validation error: {key} - {er}")
    else:
        print(data)

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