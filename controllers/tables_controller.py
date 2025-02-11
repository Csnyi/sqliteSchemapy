# controllers/tables_controller.py
import datetime
from tabulate import tabulate
from models.tables_info import Info
from models.tables.accounts import Accounts
from models.tables.users import Users

class TablesController:
    def __init__(self, db):
        self.db = db
        self.info = Info()

    def get_list(self, db_name):
        class_name = db_name.capitalize()
        rows = globals().get(class_name).fetch_all(self.db)
        header = [*(colname for colname in self.info.table_colnames[db_name])]
        table = [header]
        tablerows = [[getattr(row, attr) for attr in header] for row in rows]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))

    def add_data(self, db_table_name):
        colnames = [*(colname for colname in self.info.table_colnames[db_table_name])]
        params = dict()
        for col in colnames:
            if col == "id":
                continue
            elif col in self.info.table_timestamps[db_table_name]:
                params[col] = datetime.datetime.now()
            else:
                params[col] = input(f"{col.capitalize()}: ")
        class_name = db_table_name.capitalize()
        cls = globals().get(class_name)
        if not cls:
            raise Exception(f"The {class_name} does not exist")
        table = cls(**params)
        lastrowid = table.save(self.db)
        print(f"The data have been added to the {class_name}! Id: {lastrowid}")

    def empty_table(self, table):
        self.db.empty_table(table, self.info.table_sql)

    def accounts_list(self):
        self.get_list("accounts")

    def users_list(self):
        self.get_list("users")


    def add_data_accounts(self):
        self.add_data("accounts")

    def add_data_users(self):
        self.add_data("users")



