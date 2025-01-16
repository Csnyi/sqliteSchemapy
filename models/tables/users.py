#models/tables/users.py
class Users:
    def __init__(self, id=None, name=None, timestamp=None):
        self.id = id
        self.name = name
        self.timestamp = timestamp

    def __repr__(self):
        return f"< Users: (id={self.id!r}, name={self.name!r}, timestamp={self.timestamp!r}) >"

    @staticmethod
    def fetch_all(db):
        query = "SELECT id, name, timestamp FROM users"
        rows = db.fetchall(query)
        return [Users(*row) for row in rows]

    @staticmethod
    def fetch_one_by_id(db, id):
        query = "SELECT id, name, timestamp FROM users WHERE id = ?"
        row = db.fetchone(query, (id,))
        return Users(*row) if row else None

    def save(self, db):
        if self.id: 
            query = "UPDATE users SET name = ?, timestamp = ? WHERE id = ?"
            params = (self.name, self.timestamp, self.id)
        else: 
            query = "INSERT INTO users (id, name, timestamp) VALUES (?, ?, ?)"
            params = (self.id, self.name, self.timestamp)
        lastrowid = db.lastrowid(query, params)
        return lastrowid

    def delete(self, db):
        if self.id:
            query = "DELETE FROM users WHERE id = ?"
            db.execute(query, (self.id,))

