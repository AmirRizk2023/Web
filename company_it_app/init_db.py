import sqlite3

# الاتصال بقاعدة البيانات (هتتعمل لو مش موجودة)
conn = sqlite3.connect('company.db')
c = conn.cursor()

# جدول الموظفين
c.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    unit TEXT
)
''')

# جدول الأجهزة
c.execute('''
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    serial TEXT,
    employee_id INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees (id)
)
''')

conn.commit()
conn.close()

print("Database and tables created successfully!")
