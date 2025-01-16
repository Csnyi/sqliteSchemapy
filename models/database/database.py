# models/database.py
import sqlite3

class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def execute(self, query, params=()):
        self.cur.execute(query, params)
        self.conn.commit()

    def lastrowid(self, query, params=()):
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur.lastrowid

    def fetchone(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def fetchall(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()

    def empty_table(self, table, table_sql):
        seq = "AUTOINCREMENT"
        query = f'DELETE FROM {table}'
        self.execute(query)
        if seq in table_sql[table]:
            query_seq = "DELETE FROM 'sqlite_sequence'"
            self.execute(query_seq)
        
    def get_table_info(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.fetchall(query)]
        table_info = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA table_info({table});"
                columns = self.fetchall(query)
                table_info[table] = [{
                    'id': col[0],
                    'name': col['name'], 
                    'type': col['type'], 
                    'notnull': col['notnull'], 
                    'dflt_value': col['dflt_value'], 
                    'pk': col['pk']
                } for col in columns]
        return table_info
    
    def get_foreign_key_list(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.fetchall(query)]
        table_info = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA table_info({table});"
                columns = self.fetchall(query)
                table_info[table] = [{
                    'id': col[0],
                    'name': col['name'], 
                    'type': col['type'], 
                    'notnull': col['notnull'], 
                    'dflt_value': col['dflt_value'], 
                    'pk': col['pk']
                } for col in columns]
        return table_info
    
    def get_sql(self):
        query = 'SELECT name, sql FROM sqlite_master'
        tables = self.fetchall(query)
        table_sql = {}
        for table in tables:
            if table['name'] != 'sqlite_sequence':
                table_sql[table['name']] = table['sql']
        return table_sql
    
    def autoincrement_sequence(self):
        query = "SELECT name, seq FROM sqlite_sequence;"
        tables = self.fetchall(query)
        autoinc_seq = {}
        for table in tables:
            if table['name'] != 'sqlite_sequence':
                autoinc_seq[table['name']] = table['seq']
        return autoinc_seq
    
    def iterdump(self, file):
        with open(file, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

