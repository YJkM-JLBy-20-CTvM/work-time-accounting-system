import psycopg2
from db_connection import get_connection

conn = get_connection()

cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS departments(
        department_id SERIAL PRIMARY KEY,
        department_name VARCHAR(100) NOT NULL
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS positions(
        position_id SERIAL PRIMARY KEY,
        position_name VARCHAR(100) NOT NULL
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        employee_id SERIAL PRIMARY KEY,
        last_name VARCHAR(100) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        phone VARCHAR(20),

        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        employee_role VARCHAR(20) CHECK (employee_role IN ('employee', 'admin')) NOT NULL,

        department_id INTEGER NOT NULL,
        position_id INTEGER NOT NULL,

        FOREIGN KEY (department_id) REFERENCES departments (department_id),
        FOREIGN KEY (position_id) REFERENCES positions (position_id)
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS work_time_accounting(
        record_id SERIAL PRIMARY KEY,
        record_date DATE NOT NULL,
        arrival_time TIME,
        departure_time TIME,

        employee_id INTEGER NOT NULL,

        FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
        UNIQUE (employee_id, record_date)
    );
""")

print("База данных успешно инициализирована")

conn.commit()
cur.close()
conn.close()
