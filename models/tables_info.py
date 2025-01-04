class Info: 
    def __init__(self):
        self.table_colnames = dict()
        self.table_info = dict()
        self.table_sql = dict()

        self.table_colnames = {'accounts': ('id', 'account_number', 'balance', 'interest_rate', 'user_id', 'timestamp'), 'users': ('id', 'name', 'timestamp')}
        self.table_info = {'accounts': [{'name': 'id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 1}, {'name': 'account_number', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 0}, {'name': 'balance', 'type': 'REAL', 'notnull': 1, 'dflt_value': None, 'pk': 0}, {'name': 'interest_rate', 'type': 'REAL', 'notnull': 0, 'dflt_value': '0.0', 'pk': 0}, {'name': 'user_id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 0}, {'name': 'timestamp', 'type': 'DATETIME', 'notnull': 1, 'dflt_value': 'CURRENT_TIMESTAMP', 'pk': 0}], 'users': [{'name': 'id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 1}, {'name': 'name', 'type': 'TEXT', 'notnull': 1, 'dflt_value': None, 'pk': 0}, {'name': 'timestamp', 'type': 'DATETIME', 'notnull': 1, 'dflt_value': 'CURRENT_TIMESTAMP', 'pk': 0}]}
        self.table_sql = {'accounts': 'CREATE TABLE "accounts" (\n\t"id"\tINTEGER,\n\t"account_number"\tINTEGER,\n\t"balance"\tREAL NOT NULL,\n\t"interest_rate"\tREAL DEFAULT 0.0,\n\t"user_id"\tINTEGER,\n\t"timestamp"\tDATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n\tFOREIGN KEY("user_id") REFERENCES "users"("id"),\n\tPRIMARY KEY("id")\n)', 'users': 'CREATE TABLE "users" (\n\t"id"\tINTEGER,\n\t"name"\tTEXT NOT NULL,\n\t"timestamp"\tDATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n\tPRIMARY KEY("id" AUTOINCREMENT)\n)'}
