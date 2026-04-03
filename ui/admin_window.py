from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QDateEdit, QHBoxLayout
)
from PyQt5.QtCore import QDate
from db_connection import get_connection
from ui.employee_crud_window import EmployeeCRUD
from ui.department_crud_window import DepartmentCRUD
from ui.position_crud_window import PositionCRUD
from ui.report_window import ReportWindow
from ui.change_password_window import ChangePasswordWindow


class AdminWindow(QWidget):
    def __init__(self, admin_id):
        super().__init__()
        
        self.admin_id = admin_id

        self.setWindowTitle("Окно администратора")
        self.resize(500, 550)

        layout = QVBoxLayout()

        self.bnt_change_password = QPushButton("Сменить пароль")
        self.bnt_change_password.clicked.connect(self.open_change_password_window)
        layout.addWidget(self.bnt_change_password)

        layout.addWidget(QLabel("Выберите сотрудника:"))

        self.employee_combo = QComboBox()
        layout.addWidget(self.employee_combo)

        self.load_employees()

        date_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        date_layout.addWidget(QLabel("С:"))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("По:"))
        date_layout.addWidget(self.date_to)

        layout.addLayout(date_layout)

        self.btn_view = QPushButton("Посмотреть рабочее время")
        self.btn_view.clicked.connect(self.view_employee_time)
        layout.addWidget(self.btn_view)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.btn_crud = QPushButton("Открыть меню редактирования таблиц")
        self.btn_crud.clicked.connect(self.open_crud)
        layout.addWidget(self.btn_crud)

        self.report_btn = QPushButton("Окно отчётов")
        self.report_btn.clicked.connect(self.open_report_window)
        layout.addWidget(self.report_btn)

        self.setLayout(layout)
        
    def open_change_password_window(self):
        self.change_password_window = ChangePasswordWindow(self.admin_id)
        self.change_password_window.show()

    def load_employees(self):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT employee_id, last_name, first_name
                FROM employees
            """)

            for emp_id, last, first in cur.fetchall():
                self.employee_combo.addItem(f"{last} {first}", emp_id)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def view_employee_time(self):
        employee_id = self.employee_combo.currentData()

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT record_date, arrival_time, departure_time
                FROM work_time_accounting
                WHERE employee_id = %s
                AND record_date BETWEEN %s AND %s
                ORDER BY record_date DESC
            """, (employee_id, date_from, date_to))

            records = cur.fetchall()

            self.output.clear()
            
            total_minutes_all = 0

            for record in records:
                date, arrival, departure = record

                arrival_str = arrival.strftime("%H:%M") if arrival else "---"
                departure_str = departure.strftime("%H:%M") if departure else "---"

                if arrival and departure:
                    total_minutes = (
                        departure.hour * 60 + departure.minute
                    ) - (
                        arrival.hour * 60 + arrival.minute
                    )

                    hours = total_minutes // 60
                    minutes = total_minutes % 60

                    word_time = f"{hours} ч {minutes} мин" if hours > 0 else f"{minutes} мин"

                    total_minutes_all += total_minutes
                else:
                    word_time = "—"

                self.output.append(
                    f"{date.strftime('%d.%m.%Y')} | {arrival_str} - {departure_str} | {word_time}"
                )

            total_hours = total_minutes_all // 60
            total_minutes = total_minutes_all % 60
            
            self.output.append("\n-----------------------------------------")
            self.output.append(f"Итого за период: {total_hours} ч {total_minutes} мин")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def open_crud(self):
        self.crud_menu = QWidget()
        self.crud_menu.setWindowTitle("Выбор таблицы")
        
        layout = QVBoxLayout()
        
        btn_emp = QPushButton("Сотрудники")
        btn_dep = QPushButton("Отделы")
        btn_pos = QPushButton("Должности")
        
        btn_emp.clicked.connect(self.open_employee_crud)
        btn_dep.clicked.connect(self.open_department_crud)
        btn_pos.clicked.connect(self.open_position_crud)
        
        layout.addWidget(btn_emp)
        layout.addWidget(btn_dep)
        layout.addWidget(btn_pos)
        
        self.crud_menu.setLayout(layout)
        self.crud_menu.show()
        
    def open_employee_crud(self):
        self.employee_crud = EmployeeCRUD()
        self.employee_crud.show()
        
    def open_department_crud(self):
        self.department_crud = DepartmentCRUD()
        self.department_crud.show()
        
    def open_position_crud(self):
        self.position_crud = PositionCRUD()
        self.position_crud.show()

    def open_report_window(self):
        self.report_window = ReportWindow()
        self.report_window.show()