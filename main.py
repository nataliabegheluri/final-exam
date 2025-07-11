import sys
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem


#დიზაინის ფაილიდან ვაიმპორტებთ დიზაინს
from ui_tickets import Ui_MainWindow


#მონაცემთა ბაზის კლასი
class DatabaseManager:

    def __init__(self, db_name='tickets.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

#ვქმნით ცხრილს მონაცემების მიხედვით
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tickets
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             name TEXT NOT NULL,
                             movie TEXT NOT NULL,
                             quantity INTEGER NOT NULL)''')
        self.conn.commit()


#ახალი ბილეთის დამატება INSERT ფუნქციით
    def add_ticket(self, name, movie, quantity):
        self.cursor.execute("INSERT INTO tickets (name, movie, quantity) VALUES (?, ?, ?)",
                            (name, movie, quantity))
        self.conn.commit()

#ბილეთის წამოღება
    def get_all_tickets(self):
        self.cursor.execute("SELECT * FROM tickets")
        return self.cursor.fetchall()

#ბილეთის წაშლა აიდის მიხედვით
    def delete_ticket(self, ticket_id):
        self.cursor.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
        self.conn.commit()

#ბილეთის განახლება
    def update_ticket(self, ticket_id, name, movie, quantity):
        self.cursor.execute("UPDATE tickets SET name=?, movie=?, quantity=? WHERE id=?",
                            (name, movie, quantity, ticket_id))
        self.conn.commit()

#ბაზასთან კავშირის დახურვა
    def __del__(self):
        self.conn.close()

#მთავარი აპლიკაციის კლასი
class TicketSystem(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # UI-ს ინიციალიზაცია
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ბაზასთან კავშირი
        self.db = DatabaseManager()

        # ცხრილის დაყენება
        self.setup_table()

        # ღილაკების დაკავშირება
        self.ui.damateba.clicked.connect(self.add_ticket)
        self.ui.washla.clicked.connect(self.delete_ticket)
        self.ui.pushButton.clicked.connect(self.update_ticket)

        # საწყისი მონაცემების ჩატვირთვა
        self.load_data()

#ცხრილის კონფიგურაცია
    def setup_table(self):
        #ქმნის ახალ ვიჯეტს(ცხრილს) , პარამტრად გადაეცემა centralwidget  - მთავარი კონტეინერი.
        self.tableWidget = QtWidgets.QTableWidget(self.ui.centralwidget)
        #ზომები(Qtcore.Qrect განსაზღვრავს ვიჯეტის პოზიციას და ზომას მის მშობელ კონტეინერში)
        self.tableWidget.setGeometry(QtCore.QRect(350, 40, 420, 500))
        #სვეტები
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'სახელი', 'ფილმი', 'რაოდენობა'])
        #დამატებითი ფუნქციონალი
        #ეს ფუნქცია განსაზღვრავს თუ რა ირჩევა მომხმარებლის მიერ დაწკაპებისას(SelectRows - მთლიანი სვეტი)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #ეს ფუნქცია განსაზღვრავს თუ რამდენი ელემენტის მონიშვნაა შესაძლებელი ერთდროულად(ამ შემთხვევაში 1-ის)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)


#მონაცემების ჩატვირთვა
    def load_data(self):
        tickets = self.db.get_all_tickets()
        #ცხრილის როგების რაოდენობის დაყენება
        self.tableWidget.setRowCount(len(tickets))

        # პასუხს აგებს ცხრილში მონაცემების განლაგება/მდებარეობაზე
        for row, ticket in enumerate(tickets):
            for col, data in enumerate(ticket):
                self.tableWidget.setItem(row, col, QTableWidgetItem(str(data)))

    def get_selected_ticket_id(self):
        #არჩეული ბილეთის ID-ის მოძებნა.თუ მონიშნულია სვეტი ამ ფუნქციით გავიგებთ მის აიდის ნომერს
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            return int(self.tableWidget.item(selected_row, 0).text())
        return None

    def add_ticket(self):
        #დამატება
        name = self.ui.saxeli.text()
        quantity = self.ui.raodenoba.text()

        # ვალიდაცია
        if not name:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ შეიყვანოთ სახელი!")
            return

        if not quantity:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ შეიყვანოთ რაოდენობა!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "შეცდომა", "რაოდენობა უნდა იყოს რიცხვი!")
            return

        # ფილმის არჩევა
        if self.ui.titaniki.isChecked():
            movie = "ტიტანიკი"
        elif self.ui.forestgampi.isChecked():
            movie = "ფორესტ გამპი"
        elif self.ui.dawyeba.isChecked():
            movie = "დაწყება"
        else:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ აირჩიოთ ფილმი!")
            return

        # ბაზაში დამატება
        self.db.add_ticket(name, movie, quantity)

        # ველების გასუფთავება
        self.ui.saxeli.clear()
        self.ui.raodenoba.clear()
        self.ui.titaniki.setChecked(False)
        self.ui.forestgampi.setChecked(False)
        self.ui.dawyeba.setChecked(False)

        # ცხრილის განახლება
        self.load_data()

        QMessageBox.information(self, "დადასტურება", "ბილეთი წარმატებით დაემატა!")

    # ბილეთის წაშლა
    def delete_ticket(self):
        ticket_id = self.get_selected_ticket_id()
        if ticket_id is None:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ აირჩიოთ ბილეთი წასაშლელად!")
            return

        reply = QMessageBox.question(self, "დადასტურება",
                                     "დარწმუნებული ხართ რომ გსურთ ბილეთის წაშლა?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.delete_ticket(ticket_id)
            self.load_data()
            QMessageBox.information(self, "დადასტურება", "ბილეთი წარმატებით წაიშალა!")

    # ბილეთის განახლება
    def update_ticket(self):
        ticket_id = self.get_selected_ticket_id()
        if ticket_id is None:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ აირჩიოთ ბილეთი განსასახლებლად!")
            return

        name = self.ui.saxeli.text()
        quantity = self.ui.raodenoba.text()

        # ვალიდაცია
        if not name:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ შეიყვანოთ სახელი!")
            return

        if not quantity:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ შეიყვანოთ რაოდენობა!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "შეცდომა", "რაოდენობა უნდა იყოს რიცხვი!")
            return

        # ფილმის არჩევა
        if self.ui.titaniki.isChecked():
            movie = "ტიტანიკი"
        elif self.ui.forestgampi.isChecked():
            movie = "ფორესტ გამპი"
        elif self.ui.dawyeba.isChecked():
            movie = "დაწყება"
        else:
            QMessageBox.warning(self, "შეცდომა", "გთხოვთ აირჩიოთ ფილმი!")
            return

        # ბაზაში განახლება
        self.db.update_ticket(ticket_id, name, movie, quantity)

        # ველების გასუფთავება
        self.ui.saxeli.clear()
        self.ui.raodenoba.clear()
        self.ui.titaniki.setChecked(False)
        self.ui.forestgampi.setChecked(False)
        self.ui.dawyeba.setChecked(False)

        # ცხრილის განახლება
        self.load_data()

        QMessageBox.information(self, "დადასტურება", "ბილეთი წარმატებით განახლდა!")



if __name__ == "__main__":
    # sys.argv გადაეცემა ქომანდური ხაზის არგუმენტების მხარდაჭერისთვის
    app = QtWidgets.QApplication(sys.argv)
    # ქმნის მთავარ ფანჯარას
    window = TicketSystem()
    # აჩვენებს მთავარ ფანჯარას
    window.show()
    # გაუშვებს აპლიკაციის მოვლენათა უსასრულო ციკლს და უზრუნველყოფს სისტემური კოდის სწორად დაბრუნებას
    sys.exit(app.exec_())