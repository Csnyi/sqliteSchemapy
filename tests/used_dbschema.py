from dbschema import *

db = Database("../db/bank.db")
table = Table(db, "users")

row= fetch_one_by_id(table, 11)
print(row)
