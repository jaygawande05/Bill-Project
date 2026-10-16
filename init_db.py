import sqlite3

def init_database():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        address VARCHAR,
        gstin VARCHAR,
        mobile VARCHAR,
        bank_name VARCHAR,
        acc_no VARCHAR,
        ifsc VARCHAR
    )
    ''')

 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no INTEGER,
        date VARCHAR,
        due_date VARCHAR,
        bill_to TEXT,
        ship_to TEXT,
        buyer_gstin VARCHAR,
        transporter_id_name VARCHAR,
        trans_doc_no VARCHAR,
        transport_mode VARCHAR,
        vehicle_no VARCHAR,
        transport_from VARCHAR,
        cewb_no VARCHAR,
        multi_veh_info VARCHAR,
        portal_no VARCHAR,
        approx_distance VARCHAR,
        total_taxable FLOAT,
        total_tax FLOAT,
        grand_total FLOAT
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoice_item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        name VARCHAR,
        hsn VARCHAR,
        weight VARCHAR,
        qty FLOAT,
        rate FLOAT,
        amount FLOAT,
        FOREIGN KEY (invoice_id) REFERENCES invoice(id) ON DELETE CASCADE
    )
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS party (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL,
        address TEXT NOT NULL,
        gstin VARCHAR
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR NOT NULL UNIQUE,
        password VARCHAR NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print("Database successfully initialized!")

if __name__ == '__main__':
    init_database()