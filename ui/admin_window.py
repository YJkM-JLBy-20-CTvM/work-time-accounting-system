from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox
)
from db_connection import get_connection


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Окно администратора")
        self.resize(500, 500)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Выберите сотрудника:"))

        self.employee_combo = QComboBox()
        layout.addWidget(self.employee_combo)

        self.load_employees()

        self.btn_view = QPushButton("Посмотреть рабочее время")
        self.btn_view.clicked.connect(self.view_employee_time)
        layout.addWidget(self.btn_view)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.btn_crud = QPushButton("Открыть меню редактирования таблиц")
        self.btn_crud.clicked.connect(self.open_crud)
        layout.addWidget(self.btn_crud)

        layout.addWidget(QLabel("Сформировать отчёт:"))

        self.report_type = QComboBox()
        self.report_type.addItems(["По сотруднику", "По отделу"])
        layout.addWidget(self.report_type)

        self.btn_report = QPushButton("Сформировать")
        self.btn_report.clicked.connect(self.generate_report)
        layout.addWidget(self.btn_report)

        self.setLayout(layout)

    def load_employees(self):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT employee_id, last_name, first_name
                FROM employees
            """)

            self.employees = cur.fetchall()

            for emp in self.employees:
                emp_id, last, first = emp
                self.employee_combo.addItem(f"{last} {first}", emp_id)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def view_employee_time(self):
        employee_id = self.employee_combo.currentData()

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT record_date, arrival_time, departure_time
                FROM work_time_accounting
                WHERE employee_id = %s
                ORDER BY record_date DESC
            """, (employee_id,))

            records = cur.fetchall()

            self.output.clear()

            for record in records:
                date, arrival, departure = record

                arrival_str = arrival.strftime("%H:%M") if arrival else "---"
                departure_str = departure.strftime("%H:%M") if departure else "---"

                self.output.append(
                    f"{date} | {arrival_str} - {departure_str}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def open_crud(self):
        QMessageBox.information(self, "Информация", "Будет реализовано позже")

    def generate_report(self):
        report_type = self.report_type.currentText()
        employee_id = self.employee_combo.currentData()

        conn = get_connection()
        cur = conn.cursor()

        try:
            if report_type == "По сотруднику":
                cur.execute("""
                    SELECT record_date, arrival_time, departure_time
                    FROM work_time_accounting
                    WHERE employee_id = %s
                """, (employee_id,))

                records = cur.fetchall()

                self.output.clear()
                self.output.append("Отчёт по сотруднику:\n")

                for record in records:
                    date, arrival, departure = record

                    arrival_str = arrival.strftime("%H:%M") if arrival else "---"
                    departure_str = departure.strftime("%H:%M") if departure else "---"

                    self.output.append(
                        f"{date} | {arrival_str} - {departure_str}"
                    )

            else:
                QMessageBox.information(self, "Инфо", "Отчёт по отделу пока не реализован")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()