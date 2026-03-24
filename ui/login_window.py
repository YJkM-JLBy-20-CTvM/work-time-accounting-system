from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from db_connection import get_connection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")

        self.layout = QVBoxLayout()

        self.label_login = QLabel("Логин")
        self.input_login = QLineEdit()

        self.label_password = QLabel("Пароль")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        self.button_login = QPushButton("Войти")
        self.button_login.clicked.connect(self.login)

        self.layout.addWidget(self.label_login)
        self.layout.addWidget(self.input_login)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.input_password)
        self.layout.addWidget(self.button_login)

        self.setLayout(self.layout)

    def login(self):
        username = self.input_login.text()
        password = self.input_password.text()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT employee_id, employee_role
            FROM employees
            WHERE username = %s AND password = %s
        """, (username, password))

        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            employee_id, role = result

            QMessageBox.information(self, "Успех", f"Вход выполнен! Роль: {role}")

            # Здесь потом откроем нужное окно
            self.close()

        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")