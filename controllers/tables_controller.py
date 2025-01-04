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

    def accounts_list(self):
        accounts = Accounts.fetch_all(self.db)
        header = [*(colname for colname in self.info.table_colnames["accounts"])]
        table = [header]
        tablerows = [[getattr(col, attr) for attr in header] for col in accounts]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))

    def users_list(self):
        users = Users.fetch_all(self.db)
        header = [*(colname for colname in self.info.table_colnames["users"])]
        table = [header]
        tablerows = [[getattr(col, attr) for attr in header] for col in users]
        table.extend(tablerows)
        print(tabulate(table, headers="firstrow"))



