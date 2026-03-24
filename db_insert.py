import hashlib
from db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO departments (department_name)
        VALUES 
        ('IT'),
        ('Бухгалтерия'),
        ('Отдел кадров'),
        ('Маркетинг'),
        ('Продажи')
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO positions (position_name)
        VALUES 
        ('Разработчик'),
        ('Тестировщик'),
        ('Системный администратор'),
        ('Бухгалтер'),
        ('HR-менеджер'),
        ('Маркетолог'),
        ('Менеджер по продажам')
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("SELECT department_id FROM departments WHERE department_name='IT'")
    it_dep = cur.fetchone()[0]

    cur.execute("SELECT position_id FROM positions WHERE position_name='Системный администратор'")
    admin_pos = cur.fetchone()[0]

    cur.execute("SELECT position_id FROM positions WHERE position_name='Разработчик'")
    dev_pos = cur.fetchone()[0]

    def hash_pass(p):
        return hashlib.sha256(p.encode()).hexdigest()

    cur.execute("""
        INSERT INTO employees (
            last_name, first_name, middle_name,
            phone, username, password,
            employee_role, department_id, position_id
        )
        VALUES (
            'Admin', 'Admin', '',
            '', 'admin', %s,
            'admin', %s, %s
        )
        ON CONFLICT (username) DO NOTHING;
    """, (hash_pass("12345"), it_dep, admin_pos))

    employees = [
        ("Петров", "Альберт", "Иванович", "user01", "12345"),
        ("Савельев", "Артур", "Петрович", "frtur", "12345"),
        ("Баранов", "Аркадий", "Сидорович", "arkady11", "12345"),
    ]

    for last, first, middle, username, password in employees:
        cur.execute("""
            INSERT INTO employees (
                last_name, first_name, middle_name,
                phone, username, password,
                employee_role, department_id, position_id
            )
            VALUES (%s, %s, %s, '', %s, %s, 'employee', %s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, (
            last,
            first,
            middle,
            username,
            hash_pass(password),
            it_dep,
            dev_pos
        ))

    conn.commit()
    print("База данных заполнена начальными данными")

except Exception as e:
    print("Ошибка:", e)
    conn.rollback()

finally:
    cur.close()
    conn.close()
