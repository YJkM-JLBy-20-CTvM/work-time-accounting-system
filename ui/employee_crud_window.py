import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox
)
from db_connection import get_connection


class EmployeeCRUD(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Управление сотрудниками")
        self.resize(1000, 500)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество",
            "Телефон", "Логин", "Пароль", "Роль",
            "Отдел", "Должность"
        ])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)

        self.last_name_input = QLineEdit()
        self.first_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()

        self.role_combo = QComboBox()
        self.role_combo.addItems(["employee", "admin"])

        self.department_combo = QComboBox()
        self.position_combo = QComboBox()

        self.load_departments()
        self.load_positions()

        form_layout = QHBoxLayout()

        for label, widget in [
            ("Фамилия", self.last_name_input),
            ("Имя", self.first_name_input),
            ("Отчество", self.middle_name_input),
            ("Телефон", self.phone_input),
            ("Логин", self.username_input),
            ("Пароль", self.password_input),
            ("Роль", self.role_combo),
            ("Отдел", self.department_combo),
            ("Должность", self.position_combo)
        ]:
            form_layout.addWidget(QLabel(label))
            form_layout.addWidget(widget)

        self.add_btn = QPushButton("Добавить")
        self.update_btn = QPushButton("Изменить")
        self.delete_btn = QPushButton("Удалить")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_employee)
        self.update_btn.clicked.connect(self.update_employee)
        self.delete_btn.clicked.connect(self.delete_employee)
        self.table.cellClicked.connect(self.fill_inputs)

        self.load_data()

    def load_data(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT e.employee_id, e.last_name, e.first_name, e.middle_name,
                   e.phone, e.username, e.password, e.employee_role, d.department_name, p.position_name
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN positions p ON e.position_id = p.position_id
            ORDER BY e.employee_id
        """)

        rows = cur.fetchall()
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cur.close()
        conn.close()

    def load_departments(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT department_id, department_name FROM departments")
        self.departments = cur.fetchall()

        for dep in self.departments:
            self.department_combo.addItem(dep[1], dep[0])

        cur.close()
        conn.close()

    def load_positions(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT position_id, position_name FROM positions")
        self.positions = cur.fetchall()

        for pos in self.positions:
            self.position_combo.addItem(pos[1], pos[0])

        cur.close()
        conn.close()

    def add_employee(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not last_name or not first_name:
            QMessageBox.warning(self, "Ошибка", "Фамилия и имя обязательны")
            return
        
        if not username:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        
        if " " in username:
            QMessageBox.warning(self, "Ошибка", "Логин не должен содержать пробелы")
            return
        
        if len(username) < 4:
            QMessageBox.warning(self, "Ошибка", "Логин должен быть не менее 4 символов")
            return

        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 4 символов")
            return

        hashed_password = hashlib.sha256(
            password.encode()
        ).hexdigest()

        data = (
            last_name,
            first_name,
            self.middle_name_input.text(),
            self.phone_input.text(),
            username,
            hashed_password,
            self.role_combo.currentText(),
            self.department_combo.currentData(),
            self.position_combo.currentData()
        )

        conn = get_connection()
        cur = conn.cursor()
        
        try:
        
            cur.execute("""
                        SELECT 1 from employees WHERE username=%s
                    """, (username,))

            if cur.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                return

            cur.execute("""
                INSERT INTO employees (
                    last_name, first_name, middle_name,
                    phone, username, password, employee_role,
                    department_id, position_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)

            conn.commit()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
            
        finally:
            cur.close()
            conn.close()

        self.load_data()

    def fill_inputs(self, row, _):
        self.last_name_input.setText(self.table.item(row, 1).text())
        self.first_name_input.setText(self.table.item(row, 2).text())
        self.middle_name_input.setText(self.table.item(row, 3).text())
        self.phone_input.setText(self.table.item(row, 4).text())
        self.username_input.setText(self.table.item(row, 5).text())
        # self.password_input.setText(self.table.item(row, 6).text())
        role = self.table.item(row, 7).text()
        dep = self.table.item(row, 8).text()
        pos = self.table.item(row, 9).text()
        self.role_combo.setCurrentText(role)
        self.department_combo.setCurrentText(dep)
        self.position_combo.setCurrentText(pos)
        
    def update_employee(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
            return

        employee_id = int(self.table.item(selected, 0).text())

        data = (
            self.last_name_input.text(),
            self.first_name_input.text(),
            self.middle_name_input.text(),
            self.phone_input.text(),
            self.role_combo.currentText(),
            self.department_combo.currentData(),
            self.position_combo.currentData(),
            employee_id
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE employees
            SET last_name=%s, first_name=%s, middle_name=%s,
                phone=%s, employee_role=%s,
                department_id=%s, position_id=%s
            WHERE employee_id=%s
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        self.load_data()

    def delete_employee(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника")
            return

        employee_id = int(self.table.item(selected, 0).text())

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить сотрудника ID {employee_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM work_time_accounting WHERE employee_id=%s", (employee_id,))
            cur.execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))

            conn.commit()
            cur.close()
            conn.close()

            self.load_data()