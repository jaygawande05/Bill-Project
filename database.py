import sqlite3

def get_db_connection(db_path):
    conn = sqlite3.connect("invoices.db")
    conn.row_factory = sqlite3.Row
    return conn
