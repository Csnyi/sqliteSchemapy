# controller/generate_deleter.py

class GenerateDeleter:
    def __init__(self, db):
        self.db = db

    def get_all_foreign_keys(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.db.fetchall(query)]
        foreign_keys = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA foreign_key_list({table});"
                foreign_keys[table] = [
                    {'table': row['table'], 'from': row['from'], 'to': row['to']}
                    for row in self.db.fetchall(query)
                ]
        return foreign_keys

    def delete_data(self, table_name, record_id):
        all_foreign_keys = self.get_all_foreign_keys()
        for related_table, keys in all_foreign_keys.items():
            for fk in keys:
                if fk['table'] == table_name:
                    related_column = fk['from']
                    query = f"SELECT * FROM {related_table} WHERE {related_column} = ?"
                    related_rows = self.db.fetchall(query, (record_id,))
                    for row in related_rows:
                        self.delete_data(related_table, row['id'])
        try:
            query = f"DELETE FROM {table_name} WHERE id = ?"
            self.db.execute(query, (record_id,))
            return f"Record {record_id} deleted from {table_name}"
        except self.db.conn.IntegrityError as e:
            return f"Failed to delete record {record_id} from {table_name}: {e}"
