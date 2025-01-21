#validation/validator.py example

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
