import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout,QLabel, QLineEdit, QPushButton, QTableWidget,QTableWidgetItem, QComboBox, QTextEdit, QMessageBox,QFileDialog


BASE = "http://127.0.0.1:8000"


class app(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Облік обладнання")
        self.resize(860, 560)
        self.build_ui()

    def get_data(self, url):
        rep = requests.get(BASE + url)
        return rep.json()

    def post_data(self, url, body):
        rep = requests.post(BASE + url, json=body)
        return rep.json()

    def patch_data(self, url, body):
        rep = requests.patch(BASE + url, json=body)
        return rep.json()


    def build_ui(self):
        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук за назвою")

        self.filter_status = QComboBox()
        self.filter_status.addItems(["Всі стани", "working", "faulty", "under_repair", "decommissioned"])

        self.filter_room = QLineEdit()
        self.filter_room.setPlaceholderText("Кабінет")
        self.filter_room.setMaximumWidth(80)

        btn_load   = QPushButton("Завантажити список")
        btn_faulty = QPushButton("Несправні")

        btn_load.clicked.connect(self.load_equipment)
        btn_faulty.clicked.connect(self.load_faulty)

        row1.addWidget(self.search_input)
        row1.addWidget(self.filter_status)
        row1.addWidget(QLabel("Каб:"))
        row1.addWidget(self.filter_room)
        row1.addWidget(btn_load)
        row1.addWidget(btn_faulty)

        layout.addLayout(row1)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "Категорія", "Кабінет", "Стан", "Опис"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.clicked.connect(self.on_row_click)
        layout.addWidget(self.table)

        row2 = QHBoxLayout()

        row2.addWidget(QLabel("ID:"))
        self.id_input = QLineEdit()
        self.id_input.setMaximumWidth(60)
        row2.addWidget(self.id_input)

        row2.addWidget(QLabel("Стан:"))
        self.status_input = QComboBox()
        self.status_input.addItems(["working", "faulty", "under_repair", "decommissioned"])
        row2.addWidget(self.status_input)

        btn_update = QPushButton("Оновити стан")
        btn_update.clicked.connect(self.update_status)
        row2.addWidget(btn_update)

        row2.addWidget(QLabel("Кабінет:"))
        self.room_input = QLineEdit()
        self.room_input.setMaximumWidth(70)
        row2.addWidget(self.room_input)

        btn_move = QPushButton("Перемістити")
        btn_move.clicked.connect(self.move_equipment)
        row2.addWidget(btn_move)

        btn_hist = QPushButton("Переміщення")
        btn_hist.clicked.connect(self.show_movements)
        row2.addWidget(btn_hist)

        btn_iss = QPushButton("Проблеми")
        btn_iss.clicked.connect(self.show_issues)
        row2.addWidget(btn_iss)

        btn_stat = QPushButton("Статистика")
        btn_stat.clicked.connect(self.show_stats)
        row2.addWidget(btn_stat)

        btn_csv = QPushButton("Зберегти CSV")
        btn_csv.clicked.connect(self.save_csv)
        row2.addWidget(btn_csv)

        layout.addLayout(row2)

    def load_equipment(self):
        try:
            params = "?"
            if self.search_input.text():
                params += f"search={self.search_input.text()}&"
            if self.filter_status.currentIndex() > 0:
                params += f"status={self.filter_status.currentText()}&"
            if self.filter_room.text():
                params += f"room={self.filter_room.text()}&"

            data = self.get_data("/equipment" + params)
            self.fill_table(data)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def load_faulty(self):
        try:
            data = self.get_data("/equipment/faulty")
            self.fill_table(data)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def fill_table(self, data):
        self.table.setRowCount(0)
        for item in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item["eq_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["category"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["room"]))
            self.table.setItem(row, 4, QTableWidgetItem(item["status"]))
            self.table.setItem(row, 5, QTableWidgetItem(item.get("description", "")))

    def on_row_click(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.id_input.setText(self.table.item(row, 0).text())
        self.status_input.setCurrentText(self.table.item(row, 4).text())

    def update_status(self):
        eid = self.id_input.text().strip()
        if not eid:
            QMessageBox.warning(self, "Увага", "Введіть ID")
            return
        try:
            result = self.patch_data(f"/equipment/{eid}/status",
                                     {"status": self.status_input.currentText()})
            if "message" in result:
                QMessageBox.warning(self, "Помилка", result["message"])
            else:
                QMessageBox.information(self, "Успіх", "Стан оновлено")
                self.load_equipment()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def move_equipment(self):
        eid      = self.id_input.text().strip()
        new_room = self.room_input.text().strip()
        if not eid or not new_room:
            QMessageBox.warning(self, "Увага", "Введіть ID та кабінет")
            return
        try:
            result = self.post_data("/equipment/move",
                                    {"eq_id": int(eid), "new_room": new_room})
            if "message" in result:
                QMessageBox.warning(self, "Помилка", result["message"])
            else:
                QMessageBox.information(self, "Успіх", f"Переміщено до {new_room}")
                self.room_input.clear()
                self.load_equipment()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def show_movements(self):
        eid = self.id_input.text().strip()
        if not eid:
            QMessageBox.warning(self, "Увага", "Введіть ID")
            return
        try:
            data = self.get_data(f"/equipment/{eid}/movements")
            text = "\n".join(
                f"#{m['mov_id']}  {m['from_room']} → {m['to_room']}  ({m['reason']})"
                for m in data
            ) or "Переміщень немає"
            QMessageBox.information(self, f"Переміщення обл. #{eid}", text)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def show_issues(self):
        eid = self.id_input.text().strip()
        if not eid:
            QMessageBox.warning(self, "Увага", "Введіть ID")
            return
        try:
            data = self.get_data(f"/equipment/{eid}/issues")
            text = "\n".join(
                f"#{i['issue_id']}  [{i['severity']}]  {i['description']}  ({'вирішено' if i['resolved'] else 'активна'})"
                for i in data
            ) or "Проблем немає"
            QMessageBox.information(self, f"Проблеми обл. #{eid}", text)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def show_stats(self):
        try:
            s = self.get_data("/statistics")
            text = (
                f"Всього: {s['total']}\n"
                f"Працює: {s['working']}\n"
                f"Несправне: {s['faulty']}\n"
                f"На ремонті: {s['under_repair']}\n"
                f"Переміщень: {s['total_movements']}\n"
                f"Невирішених проблем: {s['unresolved_issues']}\n\n"
                f"По кабінетах:\n" +
                "\n".join(f"  {r}: {c}" for r, c in s["by_room"].items())
            )
            QMessageBox.information(self, "Статистика", text)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def save_csv(self):
        try:
            data = self.get_data("/equipment")
            path, _ = QFileDialog.getSaveFileName(self, "Зберегти CSV", "equipment.csv", "CSV (*.csv)")
            if not path:
                return
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("ID,Назва,Категорія,Кабінет,Стан,Опис\n")
                for item in data:
                    f.write(f"{item['eq_id']},{item['name']},{item['category']},"
                            f"{item['room']},{item['status']},{item.get('description','')}\n")
            QMessageBox.information(self, "Збережено", path)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = app()
    window.show()
    sys.exit(application.exec())