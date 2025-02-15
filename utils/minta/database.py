# templates/database.py
import sqlite3

class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute('PRAGMA foreign_keys = ON;')
    
    def execute(self, query, params=()):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Db execute error: {e}")
    
    def lastrowid(self, query, params=()):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            return self.cur.lastrowid
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Db execute error: {e}")
    
    def fetchone(self, query, params=()):
        try:
            self.cur.execute(query, params)
            return self.cur.fetchone()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Db execute error: {e}")
    
    def fetchall(self, query, params=()):
        try:
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Db execute error: {e}")
    
    def close(self):
        self.conn.close()

    def create_table(self, table, statement):
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table} ({statement})"
            self.execute(query)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Create error: {e}")
    
    def get_indexes(self):
        query = '''
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type= 'index';
        '''
        return self.fetchall(query)
    
    def create_unique_index(self, index_name, table, column):
        try:
            query = f'''CREATE UNIQUE 
            INDEX {index_name} 
            ON {table}({column});'''
            self.execute(query)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Create error: {e}")
    
    def drop_index(self, index_name):
        try:
            query = f"DROP INDEX {index_name}"
            self.execute(query)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Create error: {e}")
    
    def empty_table(self, table):
        try:
            #sequence = "AUTOINCREMENT"
            query = f"DELETE FROM {table}"
            self.execute(query)
            #table_sql = self.get_sql()
            if self.has_autoincrement(table): #sequence in table_sql[table]:
                query_seq = 'DELETE FROM "sqlite_sequence"'
                self.execute(query_seq)
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Db empty error: {e}")
    
    #table_info = {'table': [{'id': , 'name': '', 'type': '', 'notnull': , 'dflt_value': , 'pk': }, {}...], 'table': [{},{}...]}
    def get_table_info(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.fetchall(query)]
        table_info = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA table_info({table});"
                columns = self.fetchall(query)
                table_info[table] = [{'id': col[0], 'name': col['name'], 'type': col['type'], 'notnull': col['notnull'], 'dflt_value': col['dflt_value'], 'pk': col['pk']} for col in columns]
        return table_info
 
    def get_colnames(self):
        table_info = self.get_table_info()
        table_colnames = {table: tuple(col['name'] for col in columns) for table, columns in table_info.items()}
        return table_colnames
    
    def get_required_columns(self, table_name):
        query = f"PRAGMA table_info({table_name});"
        columns = self.fetchall(query)
        required_columns = [
            col["name"]
            for col in columns
            if col["dflt_value"] is None and col["pk"] == 0
        ]
        return required_columns
    
    def has_autoincrement(self, table_name):
        try:
            query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"
            result = self.fetchone(query)
            if result and result['sql']:
                create_statement = result['sql']
                return "AUTOINCREMENT" in create_statement.upper()
            return False
        except sqlite3.DatabaseError as e:
            return e
    
    def get_foreign_key_list(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.fetchall(query)]
        foreign_key_list = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA foreign_key_list({table});"
                columns = self.fetchall(query)
                foreign_key_list[table] = [{
                    'id': col[0], 
                    'seq': col['seq'], 
                    'table': col['table'], 
                    'from': col['from'], 
                    'to': col['to'], 
                    'on_update': col['on_update'], 
                    'on_delete': col['on_delete'],
                    'match': col['match']
                } for col in columns]
        return foreign_key_list
    
    def del_by_foreign_key(self, table, form_key, to_key):
        query = f"DELETE FROM {table} WHERE {form_key} = ?"
        self.execute(query, (to_key,))
    
    def delete_where(self, table, condition, params = ()):
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute(query, params)
    
    def get_sql(self):
        query = 'SELECT name, sql FROM sqlite_master'
        tables = self.fetchall(query)
        table_sql = {}
        for table in tables:
            if table["name"] != 'sqlite_sequence':
                table_sql[table["name"]] = table["sql"]
        return table_sql
    
    def backup(self, file_path):
        with open(file_path, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

    def restore(self, file_path):
        with open(file_path, "r") as f:
            sql_script = f.read()
            self.conn.executescript(sql_script)

    def drop_table(self, table_name):
        query = f"DROP TABLE {table_name}"
        self.execute(query)

    def select_inner(self, table, table_join, state, where):
        query = f"SELECT * FROM {table} INNER JOIN {table_join} ON {state} WHERE {where};"
        return self.fetchall(query)
