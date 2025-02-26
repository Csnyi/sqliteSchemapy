from dbschema import *

db = Database("../db/bank.db")
table = Table(db, "accounts")

exec_custom(table)
list_data(table)