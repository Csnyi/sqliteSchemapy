#models/tables/accounts.py
class Accounts:
    def __init__(self, id=None, account_number=None, balance=None, interest_rate=None, user_id=None, timestamp=None):
        self.id = id
        self.account_number = account_number
        self.balance = balance
        self.interest_rate = interest_rate
        self.user_id = user_id
        self.timestamp = timestamp

    def __repr__(self):
        return f"< Accounts: (id={self.id!r}, account_number={self.account_number!r}, balance={self.balance!r}, interest_rate={self.interest_rate!r}, user_id={self.user_id!r}, timestamp={self.timestamp!r}) >"

    @staticmethod
    def fetch_all(db):
        query = "SELECT id, account_number, balance, interest_rate, user_id, timestamp FROM accounts"
        rows = db.fetchall(query)
        return [Accounts(*row) for row in rows]

    @staticmethod
    def fetch_one_by_id(db, id):
        query = "SELECT id, account_number, balance, interest_rate, user_id, timestamp FROM accounts WHERE id = ?"
        row = db.fetchone(query, (id,))
        return Accounts(*row) if row else None

    def save(self, db):
        if self.id: 
            query = "UPDATE accounts SET account_number = ?, balance = ?, interest_rate = ?, user_id = ?, timestamp = ? WHERE id = ?"
            params = (self.account_number, self.balance, self.interest_rate, self.user_id, self.timestamp, self.id)
        else: 
            query = "INSERT INTO accounts (id, account_number, balance, interest_rate, user_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
            params = (self.id, self.account_number, self.balance, self.interest_rate, self.user_id, self.timestamp)
        lastrowid = db.lastrowid(query, params)
        return lastrowid

    def delete(self, db):
        if self.id:
            query = "DELETE FROM accounts WHERE id = ?"
            db.execute(query, (self.id,))

