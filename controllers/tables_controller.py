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

    def accounts_list(self):
        self.get_list("accounts")

    def users_list(self):
        self.get_list("users")



