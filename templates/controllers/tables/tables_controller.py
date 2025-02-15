import datetime
from tabulate import tabulate
from models.validation.validator import Validator

class TablesController:
    def __init__(self, db):
        self.db = db
    
    def get_list(self, table_name):
        class_name = table_name.capitalize()
        rows = globals().get(class_name)().fetch_all(self.db)
        table_colnames = self.db.get_colnames()
        header = [*(colname for colname in table_colnames[table_name])]
        table = [header]
        tablerows = [[getattr(row, attr) for attr in header] for row in rows]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))

    def add_data(self, table_name, update = None):
        table_colnames = self.db.get_required_columns(table_name)
        colnames = [*(colname for colname in table_colnames)]
        if update:
            colnames.append("id")
        params = dict()
        validator = Validator(self.db)
        table_info = validator.table_info[table_name]
        for colname in colnames:
            for col in table_info:
                if colname == col["name"] and col["type"] == "TEXT":
                    params[colname] = input(f"{colname.capitalize()}: ")
                if colname == col["name"] and col["type"] == "INTEGER":
                    params[colname] = int(input(f"{colname.capitalize()}: "))
                if colname == col["name"] and col["type"] == "REAL":
                    params[colname] = float(input(f"{colname.capitalize()}: "))
        valid_error = validator.validate_data(table_name, params)
        if valid_error != []:
            raise Exception(valid_error)
        class_name = table_name.capitalize()
        clss = globals().get(class_name)
        if not clss:
            raise Exception(f"The {class_name} does not exist")
        table = clss(**params)
        table.save(self.db)
        if update:
            return f"The {table_name} row have been updated!"
        else:
            return f"The {table_name} row have been added!"
    
    def delete(self, table_name, row_id):
        try:
            table_class = table_name.capitalize()
            clss = globals().get(table_class)()
            if not clss:
                raise Exception(f"{table_name} table not found")
            row = clss.fetch_one_by_id(self.db, row_id)
            if not row:
                raise Exception(f"{table_name} {row_id} not found!")
            row.delete(self.db)
        except Exception as e:
            raise Exception(f"DbController delete error: {e}")
    
    def delete_data(self, table_name, id):
        message = []
        class_name = table_name.capitalize()
        clss = globals().get(class_name)()
        if id == "": 
            raise Exception("Missing id!")
        table = clss.fetch_one_by_id(self.db, int(id))
        if table == None:
            raise Exception("Id not found!")
        try:
            table.delete(self.db)
        except:
            foreign_keys = self.db.get_foreign_key_list()
            if foreign_keys:
                for table_, key_list in foreign_keys.items():
                    for item in key_list:
                        if table_name == item["table"]:
                            to = [to for to in self.db.fetchone(f'SELECT {item["to"]} FROM {item["table"]} WHERE id = {id}')]
                            self.db.del_by_foreign_key(table_, item["from"], *to)
                            message.append(f'{table_} where {item["from"]} is {to} deleted!')
            table.delete(self.db)
        message.append(f"The {table_name} where id = {id} have been deleted!")
        return message

    def update(self, table_name, cols, state, params):
        try:
            class_name = table_name.capitalize()
            table = globals().get(class_name)()
            table.update(self.db, cols, state, params)
        except Exception as e:
            raise Exception(f"DbController update error: {e}")

        
