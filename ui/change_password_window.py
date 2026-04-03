import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from db_connection import get_connection


class ChangePasswordWindow(QWidget):
    def __init__(self, employee_id):
        super().__init__()

        self.employee_id = employee_id

        self.setWindowTitle("Смена пароля")
        self.resize(300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Старый пароль:"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password)

        layout.addWidget(QLabel("Новый пароль:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)

        self.btn_change = QPushButton("Сменить пароль")
        self.btn_change.clicked.connect(self.change_password)
        layout.addWidget(self.btn_change)

        self.setLayout(layout)

    def change_password(self):
        old_pass = self.old_password.text().strip()
        new_pass = self.new_password.text().strip()

        if not old_pass or not new_pass:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        if len(new_pass) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 4 символов")
            return
        
        if " " in new_pass:
            QMessageBox.warning(self, "Ошибка", "Пароль не должен содержать пробелы")
            return
 
        conn = get_connection()
        cur = conn.cursor()

        try:
            old_hash = hashlib.sha256(old_pass.encode()).hexdigest()

            cur.execute("""
                SELECT password FROM employees
                WHERE employee_id = %s
            """, (self.employee_id,))

            result = cur.fetchone()

            if not result:
                QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
                return

            if result[0] != old_hash:
                QMessageBox.warning(self, "Ошибка", "Неверный старый пароль")
                return

            new_hash = hashlib.sha256(new_pass.encode()).hexdigest()

            cur.execute("""
                UPDATE employees
                SET password = %s
                WHERE employee_id = %s
            """, (new_hash, self.employee_id))

            conn.commit()

            QMessageBox.information(self, "Успех", "Пароль изменён")

            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()