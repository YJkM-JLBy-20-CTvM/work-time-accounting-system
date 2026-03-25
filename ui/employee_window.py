from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QDateEdit, QTimeEdit,
    QMessageBox, QTextEdit, QLineEdit
)
from PyQt5.QtCore import QDate, QTime
from db_connection import get_connection
from ui.change_password_window import ChangePasswordWindow
import hashlib


class EmployeeWindow(QWidget):
    def __init__(self, employee_id):
        super().__init__()

        self.employee_id = employee_id

        self.setWindowTitle("Окно сотрудника")
        self.resize(400, 450)

        layout = QVBoxLayout()
        
        self.btn_change_password = QPushButton("Сменить пароль")
        self.btn_change_password.clicked.connect(self.open_change_password)
        
        layout.addWidget(self.btn_change_password)

        layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("Время прихода:"))
        self.arrival_time_edit = QTimeEdit()
        self.arrival_time_edit.setTime(QTime.currentTime())
        layout.addWidget(self.arrival_time_edit)

        self.btn_arrival = QPushButton("Отметить приход")
        self.btn_arrival.clicked.connect(self.mark_arrival)
        layout.addWidget(self.btn_arrival)

        layout.addWidget(QLabel("Время ухода:"))
        self.departure_time_edit = QTimeEdit()
        self.departure_time_edit.setTime(QTime.currentTime())
        layout.addWidget(self.departure_time_edit)

        self.btn_departure = QPushButton("Отметить уход")
        self.btn_departure.clicked.connect(self.mark_departure)
        layout.addWidget(self.btn_departure)

        self.btn_view = QPushButton("Просмотр рабочего времени")
        self.btn_view.clicked.connect(self.view_work_time)
        layout.addWidget(self.btn_view)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def mark_arrival(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.arrival_time_edit.time().toString("HH:mm")

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT * FROM work_time_accounting
                WHERE employee_id = %s AND record_date = %s
            """, (self.employee_id, date))

            if cur.fetchone():
                QMessageBox.warning(self, "Ошибка", "Запись за этот день уже существует")
                return

            cur.execute("""
                INSERT INTO work_time_accounting (employee_id, record_date, arrival_time)
                VALUES (%s, %s, %s)
            """, (self.employee_id, date, time))

            conn.commit()

            QMessageBox.information(self, "Успех", "Приход отмечен")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()

    def mark_departure(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.departure_time_edit.time().toString("HH:mm")

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT departure_time
                FROM work_time_accounting
                WHERE employee_id = %s AND record_date = %s
            """, (self.employee_id, date))
            
            result = cur.fetchone()
            
            if not result:
                QMessageBox.warning(self, "Ошибка", "Сначала отметьте приход")
                return
            
            if result[0] is not None:
                QMessageBox.warning(self, "Ошибка", "Уход уже отмечен")
                return
            
            cur.execute("""
                UPDATE work_time_accounting
                SET departure_time = %s
                WHERE employee_id = %s AND record_date = %s
            """, (time, self.employee_id, date))

            conn.commit()

            QMessageBox.information(self, "Успех", "Уход отмечен")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()
            
    def open_change_password(self):
        self.change_password_window = ChangePasswordWindow(self.employee_id)
        self.change_password_window.show()
                
    def view_work_time(self):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT record_date, arrival_time, departure_time
                FROM work_time_accounting
                WHERE employee_id = %s
                ORDER BY record_date DESC
            """, (self.employee_id,))

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
                        arrival.hour * 60 - arrival.minute
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
            self.output.append(f"Итого: {total_hours} ч {total_minutes} мин")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        finally:
            cur.close()
            conn.close()