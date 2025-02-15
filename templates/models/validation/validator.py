# copy -> models/validation/validator.py example

class Validator:
    def __init__(self, db):
        self.db = db
        self.table_info = self.db.get_table_info()
        # table info: (id, name, type, notnull, dflt_value, pk)
        self.foreign_key_list = self.db.get_foreign_key_list()
        # foreig key list: (id, seq, table, from, to, on_update)
    
    def info_key(self, table, key):
        return [info[key] for info in self.table_info[table]]

    def info_all(self, table):
        return [[{k: v} for k, v in info.items()] for info in self.table_info[table]]

    def get_foreign_key_list_all(self):
        return self.foreign_key_list
    
    def get_foreign_key_list_by_key(self, table, key):
        if not self.foreign_key_list[table]:
            raise Exception("Foreign key not found!")
        return [fkey[key] for fkey in self.foreign_key_list[table]]

    def validate_data(self, table_name, data):
        errors = []
        if table_name not in self.table_info:
            return [f"Table '{table_name}' does not exist in the schema."]
        
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
                    errors.append(f"Missing required field '{col_name}'.")
                continue
    
            value = data[col_name]
    
            # Ellenőrizd, hogy az érték nem NULL, ha kötelező
            if notnull and value is None:
                errors.append(f"Field '{col_name}' cannot be NULL.")
    
            # Ellenőrizd az adattípust (egyszerűsített példa)
            if col_type.upper() == "INTEGER" and not isinstance(value, int):
                errors.append(f"Field '{col_name}' must be an integer number.")
            elif col_type.upper() == "REAL" and not isinstance(value, float):
                errors.append(f"Field '{col_name}' must be a float number.")
            elif col_type.upper() == "TEXT" and not isinstance(value, str):
                errors.append(f"Field '{col_name}' must be a string.")
            elif col_type.upper() == "BOOLEAN" and not isinstance(value, int):
                errors.append(f"Field '{col_name}' must be a 1 or 0.")
    
            # Elsődleges kulcs validáció (csak ha szükséges)
            if pk and value is None:
                errors.append(f"Primary key field '{col_name}' cannot be NULL.")
    
        return errors