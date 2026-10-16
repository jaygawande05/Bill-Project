import sqlite3

conn = sqlite3.connect('invoice.db')
cursor = conn.cursor()


cursor.execute('''
INSERT OR IGNORE INTO user (username, password)
VALUES ('admin', 'pbkdf2:admin123')
''')


cursor.execute('''
INSERT INTO company (name, address, gstin, mobile, bank_name, acc_no, ifsc)
VALUES ('ABC Enterprises', 'Plot 12, Industrial Area, Mumbai', '27AAAAA0000A1Z5', '9876543210', 'HDFC Bank', '123456789012', 'HDFC0001234')
''')


cursor.execute('''
INSERT INTO party (name, address, gstin)
VALUES ('XYZ Traders', 'Shop 4, Market Yard, Pune', '27BBBBB1111B1Z2')
''')


cursor.execute('''
INSERT INTO invoice (
    invoice_no, date, due_date, bill_to, ship_to, buyer_gstin,
    total_taxable, total_tax, grand_total
) VALUES (
    101, '2026-09-11', '2026-09-20', 'XYZ Traders, Pune', 'XYZ Traders, Pune', '27BBBBB1111B1Z2',
    1000.0, 180.0, 1180.0
)
''')

invoice_id = cursor.lastrowid  


cursor.execute('''
INSERT INTO invoice_item (invoice_id, name, hsn, weight, qty, rate, amount)
VALUES (?, 'Product A', '8471', '10kg', 2.0, 500.0, 1000.0)
''', (invoice_id,))

conn.commit()


cursor.execute("SELECT id, invoice_no, grand_total FROM invoice")
print("Invoices in DB:", cursor.fetchall())

conn.close()
print("Sample data successfully inserted!")