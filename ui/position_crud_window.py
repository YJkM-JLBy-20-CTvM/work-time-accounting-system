from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox
)
from db_connection import get_connection


class PositionCRUD(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Должности")
        self.resize(500, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название"])

        self.name_input = QLineEdit()

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Название"))
        form_layout.addWidget(self.name_input)

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

        self.add_btn.clicked.connect(self.add_position)
        self.update_btn.clicked.connect(self.update_position)
        self.delete_btn.clicked.connect(self.delete_position)
        self.table.cellClicked.connect(self.fill_input)

        self.load_data()

    def load_data(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM positions ORDER BY position_id")
        rows = cur.fetchall()

        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cur.close()
        conn.close()

    def fill_input(self, row, _):
        self.name_input.setText(self.table.item(row, 1).text())

    def add_position(self):
        name = self.name_input.text()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO positions (position_name) VALUES (%s)",
            (name,)
        )

        conn.commit()
        cur.close()
        conn.close()

        self.load_data()

    def update_position(self):
        selected = self.table.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        pos_id = int(self.table.item(selected, 0).text())
        name = self.name_input.text()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE positions SET position_name=%s WHERE position_id=%s",
            (name, pos_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        self.load_data()

    def delete_position(self):
        selected = self.table.currentRow()

        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        pos_id = int(self.table.item(selected, 0).text())

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить должность ID {pos_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM positions WHERE position_id=%s", (pos_id,))

            conn.commit()
            cur.close()
            conn.close()

            self.load_data()