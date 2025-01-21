#models/tables/users.py example
class Users:
    def __init__(self, id=None, name=None, timestamp=None, valid=None):
        self.id = id
        self.name = name
        self.timestamp = timestamp
        self.valid = valid

    def __repr__(self):
        return f"< Users: (id={self.id!r}, name={self.name!r}, timestamp={self.timestamp!r}, valid={self.valid}) >"

    @staticmethod
    def fetch_all(db):
        query = "SELECT id, name, timestamp, valid FROM users"
        rows = db.fetchall(query)
        return [Users(*row) for row in rows]

    @staticmethod
    def fetch_one_by_id(db, id):
        query = "SELECT id, name, timestamp, valid FROM users WHERE id = ?"
        row = db.fetchone(query, (id,))
        return Users(*row) if row else None

    def save(self, db):
        required_columns = db.get_required_columns("users")
        params = [getattr(self, col) for col in required_columns]
        if self.id: 
            set_str = ", ".join(f"{col} = ?" for col in required_columns)
            query = f"UPDATE users SET {set_str} WHERE id = ?"
            params.append(self.id)
        else: 
            columns_str = ", ".join(required_columns)
            placeholders = ", ".join("?" for _ in required_columns)
            query = f"INSERT INTO users ({columns_str}) VALUES ({placeholders});"
        db.execute(query, params)

    def delete(self, db):
        if self.id:
            try:
                query = "DELETE FROM users WHERE id = ?"
                db.execute(query, (self.id,))
            except db.conn.IntegrityError as e:
                return None
