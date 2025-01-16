# validation/validator.py

class Validator:
    def  __init__(self, db):
        self.db = db
        self.table_info = self.db.get_table_info()
        # table info: ('id', 'name', 'type', 'notnull', 'dflt_value', 'pk')
        self.foreign_key_list = self.db.get_foreign_key_list()
        # foreign key list: ('id', 'seq', 'table', 'from', 'to', 'on_update')

    def validate_data(self, table_name, data):
        errors = []
        if table_name not in self.table_info:
            return [f"Table '{table_name}' does not exist in the schema."]
        
        schema = self.table_info[table_name]
        for column in schema:
            col_id = column['id']
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
            if col_type.upper() in ["INTEGER", "REAL"] and not isinstance(value, (int, float)):
                errors.append(f"Field '{col_name}' must be a number.")
            elif col_type.upper() == "TEXT" and not isinstance(value, str):
                errors.append(f"Field '{col_name}' must be a string.")

            # Elsődleges kulcs validáció (csak ha szükséges)
            if pk and value is None:
                errors.append(f"Primary key field '{col_name}' cannot be NULL.")

        return errors

    def has_autoincrement(self):
        result = self.db.get_sql()
        if result:
            create_statement = [val for key, val in result.items()]
            return "AUTOINCREMENT" in str(create_statement).upper()
        return False

    def get_autoincrement_sequence(self):
        result = self.db.autoincrement_sequence()
        return result if result else None

    def get_foreign_key_list(self):
        ...