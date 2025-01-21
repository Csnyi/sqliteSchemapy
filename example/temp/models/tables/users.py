#temp/models/tables/users.py example
class Users:
    def __init__(self, id=None, name=None, timestamp=None, valid=None):
        self.id = id
        self.name = name
        self.timestamp = timestamp
        self.valid = valid

    def __repr__(self):
        return f"< Users: (id={self.id!r}, name={self.name!r}, timestamp={self.timestamp!r}, valid={self.valid!r}) >"

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
        if self.id: 
            query = "UPDATE users SET name = ?, valid = ? WHERE id = ?"
            params = (self.name, self.valid, self.id)
        else: 
            query = "INSERT INTO users (id, name, valid) VALUES (?, ?, ?)"
            params = (self.id, self.name, self.valid)
        db.execute(query, params)

    def delete(self, db):
        if self.id:
            query = "DELETE FROM users WHERE id = ?"
            db.execute(query, (self.id,))

