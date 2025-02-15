# copy -> models/tables/table.py

class Table:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fetch_all(self, db):
        try:
            query = f"SELECT * FROM {self.table}"
            rows = db.fetchall(query)
            return [self.__class__(*row) for row in rows]
        except Exception as e:
            raise Exception(f"Fetch all error: {e}")

    def fetch_one_by_id(self, db, id):
        try:
            query = f"SELECT * FROM {self.table} WHERE id = ?"
            row = db.fetchone(query, (id,))
            return self.__class__(*row) if row else None
        except Exception as e:
            raise Exception(f"Fetch one error: {e}")

    def save(self, db):
        required_columns = db.get_required_columns(self.table)
        params = [getattr(self, col) for col in required_columns]
        if self.id: 
            set_str = ", ".join(f"{col} = ?" for col in required_columns)
            query = f"UPDATE {self.table} SET {set_str} WHERE id = ?"
            params.append(self.id)
        else: 
            columns_str = ", ".join(required_columns)
            placeholders = ", ".join("?" for _ in required_columns)
            query = f"INSERT INTO {self.table} ({columns_str}) VALUES ({placeholders});"
        db.execute(query, params)
    
    def delete(self, db):
        if self.id:
            try:
                query = f"DELETE FROM {self.table} WHERE id = ?"
                db.execute(query, (self.id,))
            except db.conn.Error as e:
                raise Exception(f"{self.table} delete error: {e}")

    def update(self, db, cols, state, params):
        try:
            set_str = ", ".join(f"{col} = ?" for col in cols)
            query = f"UPDATE {self.table} SET {set_str} WHERE {state}"  
            db.execute(query, params)
        except db.conn.Error as e:
                raise Exception(f"{self.table} update error: {e}")

