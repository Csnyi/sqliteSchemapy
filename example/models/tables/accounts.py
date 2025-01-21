#models/tables/accounts.py example
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
        required_columns = db.get_required_columns("accounts")
        params = [getattr(self, col) for col in required_columns]
        if self.id: 
            set_str = ", ".join(f"{col} = ?" for col in required_columns)
            query = f"UPDATE accounts SET {set_str} WHERE id = ?"
            params.append(self.id)
        else: 
            columns_str = ", ".join(required_columns)
            placeholders = ", ".join("?" for _ in required_columns)
            query = f"INSERT INTO accounts ({columns_str}) VALUES ({placeholders});"
        db.execute(query, params)

    def delete(self, db):
        if self.id:
            try:
                query = "DELETE FROM accounts WHERE id = ?"
                db.execute(query, (self.id,))
            except db.conn.IntegrityError as e:
                raise Exception(e)
