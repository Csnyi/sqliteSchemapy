import sqlite3
import argparse
import configparser
import textwrap
import datetime

class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # Támogatja a szótárszerű lekérdezést
        self.cur = self.conn.cursor()

    def execute(self, query, params=()):
        self.cur.execute(query, params)
        self.conn.commit()

    def fetchone(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def fetchall(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def iterdump(self, file):
        with open(file, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

    def get_table_info(self):
        """Lekérdezi az adatbázis összes táblájának metaadatait."""
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [row['name'] for row in self.fetchall(query)]
        table_info = {}
        for table in tables:
            if table != "sqlite_sequence":
                query = f"PRAGMA table_info({table});"
                columns = self.fetchall(query)
                table_info[table] = [(col['name'], col['type'], col['notnull'], col['dflt_value'], col['pk']) for col in columns]
        return table_info

    def close(self):
        self.conn.close()

def generate_model_classes(db):
    """Model osztályokat generál az adatbázis táblái alapján."""
    table_info = db.get_table_info()
    models = {}

    for table, columns in table_info.items():
        # Osztály neve nagybetűs formában
        class_name = table.capitalize()

        # Oszlopok és alapértelmezett értékek előkészítése
        init_args = ', '.join([f"{col[0]}=None" for col in columns])
        attributes = [col[0] for col in columns]
        init_body = "".join([f"self.{attr} = {attr}\n        " for attr in attributes])
        update_set = ", ".join([f"{attr} = ?" for attr in attributes if attr != 'id'])
        update_param = ", ".join([f"self.{attr}" for attr in attributes if attr != 'id'])
        insert_set = ", ".join(attributes)
        insert_val = ", ".join(["?" for _ in attributes])
        attrs = ", ".join([f"{attr}={{self.{attr}!r}}" for attr in attributes])
        insert_param = ", ".join([f"self.{attr}" for attr in attributes])

        # Dinamikus osztály létrehozása
        class_template = f"""
class {class_name}:
    def __init__(self, {init_args}):
        {init_body}

    def __repr__(self):
        return f"<{class_name}({attrs})>"

    @staticmethod
    def fetch_all(db):
        query = "SELECT * FROM {table}"
        rows = db.fetchall(query)
        return [{class_name}(**row) for row in rows]

    def save(self, db):
        if self.id:  # Frissítés
            query = "UPDATE {table} SET {update_set} WHERE id = ?"
            params = ({update_param}, self.id)
        else:  # Beszúrás
            query = "INSERT INTO {table} ({insert_set}) VALUES ({insert_val})"
            params = ({insert_param})
        db.execute(query, params)

    def delete(self, db):
        if self.id:
            query = "DELETE FROM {table} WHERE id = ?"
            db.execute(query, (self.id,))
"""
        exec(class_template, globals())
        models[table] = eval(class_name)

    return models

db = Database("db/bank.db")
table_info = db.get_table_info()
# Automatikus model generálás
models = generate_model_classes(db)
#print(table_info)

# Példa a 'users' táblához generált model osztály használatára
Users = models['users']
Accounts = models["accounts"]

# Összes rekord lekérdezése
all_users = Users.fetch_all(db)
# Új rekord hozzáadása 
user_name = input("User name: ")

# Ellenőrizzük, hogy létezik-e már a felhasználó
existing_user = next((user for user in all_users if user.name == user_name), None)

if existing_user:
    print(f"{user_name} already exists!")
else:
    timestamp = datetime.datetime.now()
    user = Users(name=user_name, timestamp=timestamp)
    user.save(db)
    print(f"{user_name} has been added!")

print(*Users.fetch_all(db), sep="\n")
print(*Accounts.fetch_all(db), sep="\n")

db.close()
