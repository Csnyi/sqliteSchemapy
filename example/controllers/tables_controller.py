# controllers/tables_controller.py example
import datetime
from tabulate import tabulate
from models.tables.accounts import Accounts
from models.tables.users import Users

class TablesController:
    def __init__(self, db):
        self.db = db

    def get_list(self, db_name):
        class_name = db_name.capitalize()
        rows = globals().get(class_name).fetch_all(self.db)
        table_colnames = self.db.get_colnames()
        header = [*(colname for colname in table_colnames[db_name])]
        table = [header]
        tablerows = [[getattr(row, attr) for attr in header] for row in rows]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))

    def add_data(self, db_table_name, update = None):
        table_colnames = self.db.get_required_columns(db_table_name)
        colnames = [*(colname for colname in table_colnames)]
        if update:
            colnames.append("id")
        params = dict()
        for col in colnames:
            params[col] = input(f"{col.capitalize()}: ")
        class_name = db_table_name.capitalize()
        clss = globals().get(class_name)
        if not clss:
            raise Exception(f"The {class_name} does not exist")
        table = clss(**params)
        table.save(self.db)
        if update:
            return f"The {db_table_name} row have been updated!"
        else:
            return f"The {db_table_name} row have been added!"
    
    def delete_data(self, db_table_name, id):
        message = []
        class_name = db_table_name.capitalize()
        clss = globals().get(class_name)
        if id == "":
            raise Exception("Missing id!")
        table = clss.fetch_one_by_id(self.db, int(id))
        if table == None:
            raise Exception("Id not found!")
        table_delete = table.delete(self.db)
        if table_delete == None:
            foreign_keys = self.db.get_foreign_key_list()
            if foreign_keys:
                for table_, key_list in foreign_keys.items():
                    for item in key_list:
                        if db_table_name == item["table"]:
                            to = self.db.fetchone(f'SELECT {item["to"]} FROM {item["table"]} WHERE id = {id}')
                            message.append(self.db.del_all_by_foreign_key(table_, item["from"], *to))
            table.delete(self.db)
        message.append(f"The {db_table_name} have been deleted!")
        return message
    
    def empty_table(self, table):
        self.db.empty_table(table)

