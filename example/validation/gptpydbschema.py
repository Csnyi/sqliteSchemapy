def validate_data(table_name, data, table_info):
    errors = []
    if table_name not in table_info:
        return [f"Table '{table_name}' does not exist in the schema."]
    
    schema = table_info[table_name]
    for column in schema:
        col_name = column['name']
        col_type = column['type']
        notnull = column['notnull']
        dflt_value = column['dflt_value']
        pk = column['pk']

        # Ellenőrizd, hogy az oszlop létezik-e az adatokban
        if col_name not in data:
            if notnull and dflt_value is None:
                errors.append(f"Missing required field '{col_name}'.")
            continue

        value = data[col_name]

        # Ellenőrizd, hogy az érték nem NULL, ha kötelező
        if notnull and value is None:
            errors.append(f"Field '{col_name}' cannot be NULL.")

        # Ellenőrizd az adattípust (egyszerűsített példa)
        if col_type.upper() == "INTEGER" and not isinstance(value, int):
            errors.append(f"Field '{col_name}' must be an integer number.")
        elif col_type.upper() == "REAL" and not isinstance(value, float):
            errors.append(f"Field '{col_name}' must be a float number.")
        elif col_type.upper() == "TEXT" and not isinstance(value, str):
            errors.append(f"Field '{col_name}' must be a string.")
        elif col_type.upper() == "BOOLEAN" and not isinstance(value, int):
            errors.append(f"Field '{col_name}' must be a 1 or 0.")

        # Elsődleges kulcs validáció (csak ha szükséges)
        if pk and value is None:
            errors.append(f"Primary key field '{col_name}' cannot be NULL.")

    return errors
    
# Feltételezett táblainformáció
table_info = {'accounts': [{'id': 0, 'name': 'id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 1}, {'id': 1, 'name': 'account_number', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 0}, {'id': 2, 'name': 'balance', 'type': 'REAL', 'notnull': 1, 'dflt_value': None, 'pk': 0}, {'id': 3, 'name': 'interest_rate', 'type': 'REAL', 'notnull': 0, 'dflt_value': '0.0', 'pk': 0}, {'id': 4, 'name': 'user_id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 0}, {'id': 5, 'name': 'timestamp', 'type': 'DATETIME', 'notnull': 0, 'dflt_value': 'CURRENT_TIMESTAMP', 'pk': 0}], 'users': [{'id': 0, 'name': 'id', 'type': 'INTEGER', 'notnull': 0, 'dflt_value': None, 'pk': 1}, {'id': 1, 'name': 'name', 'type': 'TEXT', 'notnull': 1, 'dflt_value': None, 'pk': 0}, {'id': 2, 'name': 'timestamp', 'type': 'DATETIME', 'notnull': 0, 'dflt_value': 'CURRENT_TIMESTAMP', 'pk': 0}, {'id': 3, 'name': 'valid', 'type': 'BOOLEAN', 'notnull': 0, 'dflt_value': '1', 'pk': 0}]}
       

# Validálandó adat
data = {
    "id": 1,
    "name": "test_user",
    'balance': 3450,
    "interest_rate": 0.03
}

# Validáció
errors = validate_data("accounts", data, table_info)
if errors:
    print("Validation errors:", errors)
else:
    print("Data is valid.")

def has_autoincrement(db_connection, table_name):
    query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    result = db_connection.execute(query).fetchone()
    if result and result['sql']:
        create_statement = result['sql']
        return "AUTOINCREMENT" in create_statement.upper()
    return False

import sqlite3

# Adatbázis kapcsolat létrehozása
conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

# Tábla létrehozása
conn.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pass BOOLEAN DEFAULT 1,
    username TEXT NOT NULL
);
""")

# Ellenőrzés
if has_autoincrement(conn, "users"):
    print("The 'id' column has AUTOINCREMENT.")
else:
    print("The 'id' column does not have AUTOINCREMENT.")

def get_autoincrement_sequence(db_connection, table_name):
    query = f"SELECT seq FROM sqlite_sequence WHERE name='{table_name}';"
    result = db_connection.execute(query).fetchone()
    return result['seq'] if result else None

'''
Az sqlite_sequence tartalmát teljesen törölheted, ha újra akarod indítani az AUTOINCREMENT értékeket:
DELETE FROM sqlite_sequence;
Vagy csak egy adott tábla értékét nullázhatod:
DELETE FROM sqlite_sequence WHERE name = 'users';
'''

'''
Az SQLite adatbázisban az idegen kulcsok struktúráját
a PRAGMA foreign_key_list(<table_name>) parancs segítségével érheted el.
Ez visszaadja, hogy egy adott tábla milyen idegen kulcsokat tartalmaz.

Példa lekérdezés:

PRAGMA foreign_key_list('orders');

Eredmény (példa):

+-------+----------+----------+-----------+---------+----------+
| id    | seq      | table    | from      | to      | on_update|
+-------+----------+----------+-----------+---------+----------+
| 0     | 0        | users    | user_id   | id      | NO ACTION|
+-------+----------+----------+-----------+---------+----------+

Ez azt jelenti:
Az orders tábla user_id oszlopa a users tábla id oszlopára hivatkozik.
'''

def validate_foreign_key(db_connection, table_name, column_name, referenced_table, referenced_column, value):
    """
    Ellenőrzi, hogy egy FOREIGN KEY érték létezik-e a hivatkozott táblában.
    """
    query = f"""
        SELECT 1
        FROM {referenced_table}
        WHERE {referenced_column} = ?
        LIMIT 1;
    """
    result = db_connection.execute(query, (value,)).fetchone()
    if result:
        return True  # Az érték érvényes
    return False  # Az érték nem található a hivatkozott táblában

def validate_multiple_foreign_keys(db_connection, table_name, column_name, referenced_table, referenced_column, values):
    """
    Több érték egyszerre validálása egy FOREIGN KEY oszlop esetén.
    """
    placeholders = ", ".join("?" for _ in values)
    query = f"""
        SELECT DISTINCT {referenced_column}
        FROM {referenced_table}
        WHERE {referenced_column} IN ({placeholders});
    """
    result = db_connection.execute(query, values).fetchall()
    valid_values = {row[referenced_column] for row in result}
    invalid_values = set(values) - valid_values
    return valid_values, invalid_values

'''
Ha a FOREIGN KEY-ek engedélyezve vannak
az SQLite-ban (alapértelmezésben nem aktívak!),
akkor az SQLite automatikusan biztosítja a referenciális integritást.
Ha érvénytelen user_id értéket próbálsz beszúrni, az SQLite hibát dob.

Engedélyezés:
PRAGMA foreign_keys = ON;
'''

def get_required_columns(db_connection, table_name):
    """
    Lekéri azokat az oszlopokat, amelyekhez explicit értéket kell megadni az INSERT során.
    """
    query = f"PRAGMA table_info({table_name});"
    columns = db_connection.execute(query).fetchall()
    required_columns = [
        col["name"]
        for col in columns
        if col["dflt_value"] is None and col["pk"] == 0
    ]
    return required_columns

def get_all_columns(db_connection, table_name):
    query = f"PRAGMA table_info({table_name});"
    columns = db_connection.execute(query).fetchall()
    all_columns = [
        col["name"]
        for col in columns
    ]
    return all_columns

'''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
CREATE TABLE "accounts" (
	"id"	INTEGER,
	"account_number"	INTEGER,
	"balance"	REAL NOT NULL,
	"interest_rate"	REAL DEFAULT 0.0,
	"user_id"	INTEGER,
	"valid" BOOLEAN DEFAULT 1,
	"timestamp"	DATETIME DEFAULT (datetime('now','localtime')),
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
""")
conn.commit()

required_columns = get_required_columns(conn, "accounts")
print(required_columns)

def generate_insert_query(table_name, required_columns):
    """
    Dinamikus INSERT lekérdezés generálása a kötelező oszlopok alapján.
    """
    columns_str = ", ".join(required_columns)
    placeholders = ", ".join("?" for _ in required_columns)
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});"
    return query

insert_query = generate_insert_query("accounts", required_columns)
print(insert_query)

params = []
for col in required_columns:
    params.append(int(input(f"{col}: ")))

cur.execute(insert_query, params)
conn.commit()

result = cur.execute('SELECT * FROM  accounts').fetchall()
all_columns = get_all_columns(conn, "accounts")
print(all_columns)
print([[row[attr] for attr in all_columns] for row in result])

result = get_autoincrement_sequence(conn, 'accounts')
print('accounts seq: ', result)

class RowWrapper:
    def __init__(self, row, columns):
        for col, value in zip(columns, row):
            setattr(self, col, value)

rows = cur.execute("SELECT * FROM accounts").fetchall()
columns = [desc[0] for desc in cur.description]
wrapped_rows = [RowWrapper(row, columns) for row in rows]
print([[getattr(row, attr) for attr in columns] for row in wrapped_rows])
