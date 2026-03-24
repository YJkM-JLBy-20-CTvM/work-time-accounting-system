import hashlib
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QMessageBox
)
from db_connection import get_connection
from ui.employee_window import EmployeeWindow
from ui.admin_window import AdminWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        
        layout = QVBoxLayout()

        self.layout = QVBoxLayout()

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Логин")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Пароль")
        self.input_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_login)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.input_login)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.input_password)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def check_login(self):
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите данные")
            return

        # hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT employee_id, employee_role
                FROM employees
                WHERE username = %s AND password = %s
            """, (username, password)) #hashed_password

            user = cur.fetchone()

            if user:
                employee_id, role = user

                QMessageBox.information(self, "Успех", f"Вы вошли как {role}")

                self.open_main_window(role, employee_id)

            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def open_main_window(self, role, employee_id):
        if role == "employee":
            self.window = EmployeeWindow(employee_id)
        elif role == "admin":
            self.window = AdminWindow()
        else:
            QMessageBox.warning(self, "Ошибка", "Неизвестная роль")
            return

        self.window.show()
        self.close()