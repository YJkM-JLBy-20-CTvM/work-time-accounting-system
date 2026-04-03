import hashlib
from db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO departments (department_name)
        VALUES 
        ('Бухгалтерия'),
        ('Отдел кадров'),
        ('Маркетинг'),
        ('Продажи')
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO positions (position_name, department_id)
        VALUES 
        ('Разработчик', '1'),
        ('Тестировщик', '1'),
        ('Бухгалтер', '2'),
        ('HR-менеджер', '3'),
        ('Маркетолог', '4'),
        ('Менеджер по продажам', '5')
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
        ("Петров", "Альберт", "Иванович", "89008007766", "user01", "12345"),
        ("Савельев", "Артур", "Петрович", "89008007767", "user02", "12345"),
        ("Баранов", "Аркадий", "Сидорович", "89008007768", "user03", "12345"),
    ]

    for last, first, middle, phone, username, password in employees:
        cur.execute("""
            INSERT INTO employees (
                last_name, first_name, middle_name,
                phone, username, password,
                employee_role, department_id, position_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'employee', %s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, (
            last,
            first,
            middle,
            phone,
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
