# copy -> controllers/database/db_controller.py
from controllers.tables.tables_controller import TablesController

class DbController(TablesController):
    def __init__(self, db):
        self.db = db

    def empty_table(self, table_name):
        try:
            self.db.empty_table(table_name)
        except Exception as e:
            raise Exception(f"DbController empty error: {e}")

    def check_foreign_key(self, reference_table):
        foreign_key_list = self.db.get_foreign_key_list()
        values = []
        if any(foreign_key_list.values()):
            for table, keys in foreign_key_list.items():
                if keys:
                    for fk in keys:
                        if fk["table"] == reference_table:
                            values.append(f'{table}.{fk["from"]} = {fk["table"]}.{fk["to"]}')
            return values
        else:
            return None

    def restore(self, file_path):
        try:
            table_info = self.db.get_table_info()
            if table_info:
                tables = [table for table in table_info]
                for table in tables:
                    self.db.drop_table(table)
            self.db.restore(file_path)
        except Exception as e:
            raise Exception(f"DbController restore error: {e}")


