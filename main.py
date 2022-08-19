import sys
import sqlite3
import buffer
from PyQt5 import QtWidgets
from Edit import Ui_Edit_Form
from Database import Ui_Database
from Login_menu import Ui_Login_menu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem

db = sqlite3.connect("Ballistic.db")                #Connection on SQL Base
curs = db.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS users (      
        login TEXT,
        password TEXT
)""")                                                #Creating table of users
db.commit()


class Authorization(QtWidgets.QMainWindow):     #Authorization class, calling auth form and check having account
    def __init__(self):
        super(Authorization, self).__init__()
        self.Login_menu = Ui_Login_menu()
        self.Login_menu.setupUi(self)
        self.work_ui()

    def work_ui(self):                                  #Buttons
        self.Login_menu.Login.clicked.connect(self.auth)
        self.Login_menu.add_user.clicked.connect(self.register)

    def auth(self):                                     #Auth function with ckeck having user in database
        self.hide()
        buffer.login = self.Login_menu.Login_place.text()
        print(buffer.login)
        user_login = self.Login_menu.Login_place.text()
        user_password = self.Login_menu.Password_place.text()

        curs.execute("SELECT * FROM users WHERE login = ?", (user_login,))
        if curs.fetchone() is None:
            QMessageBox.about(self, " ", "Такой пользователь не зарегистророван!")
        else:
            curs.execute("SELECT * FROM users WHERE login = ? AND password = ?", (user_login, user_password,))
            if curs.fetchone() is None:
                QMessageBox.about(self, " ", "Неверный логин или пароль!")
            else:
                self.Database = Data()
                self.Database.show()

    def register(self):                         #if user exsistn`t then this function registering of him
        user_login = self.Login_menu.Login_place.text()
        buffer.login = user_login
        user_password = self.Login_menu.Password_place.text()
        curs.execute("INSERT INTO users VALUES (?, ?)", (user_login, user_password))
        for value in curs.execute("SELECT * FROM users"):
            print(value)
        db.commit()
        curs.execute("""CREATE TABLE IF NOT EXISTS {} (Date_of date, shoots int, point_2 int, 
                    point_3 int, point_4 int, point_5 int, PercentageOfHits int, Note text, ID int)""".format(
            user_login))
        db.commit()
        for value in curs.execute("SELECT * FROM {}".format(user_login)):
            print(value)


class Data(QtWidgets.QMainWindow):              #Class for working with SQL database adding and editing recordings
    def __init__(self):
        super(Data, self).__init__()
        self.Database = Ui_Database()
        self.Database.setupUi(self)
        self.upload()
        self.Database.user.setText(buffer.login)
        self.Database.add.clicked.connect(self.registartion)
        self.deleteItem()
        self.Database.delete_2.clicked.connect(self.deleteItem)
        self.Database.update.clicked.connect(self.upload)
        self.Database.exit.clicked.connect(self.exit)

    def upload(self):                   #Upload data from SQL database in table of form created on pyqt5
        curs.execute("SELECT Count(*) FROM {}".format(buffer.login))
        injck = curs.fetchone()
        count = int(injck[0])
        self.Database.table.setRowCount(count)
        curs.execute("SELECT * FROM {}".format(buffer.login))
        row = 0
        for value in curs:
            for col in range(8):
                print(value[col])
                self.Database.table.setItem(row, col, QTableWidgetItem(str(value[col])))
            row = + 1

    def registartion(self):
        self.Edit = Editor()
        self.Edit.show()

    def deleteItem(self):
        row = self.Database.table.currentRow()
        print(row)
        sql_update_query = """DELETE from {} where ID = ?""".format(buffer.login)
        curs.execute(sql_update_query, (row,))
        db.commit()

    def exit(self):
        self.close()


class Editor(Data, QtWidgets.QMainWindow):
    def __init__(self):
        super(Editor, self).__init__()
        self.Edit = Ui_Edit_Form()
        self.Edit.setupUi(self)
        self.Edit.Save.clicked.connect(self.listening)

    def listening(self):                #Adding new recordings in database
        date = self.Edit.dateEdit.text()
        shoots = self.Edit.spinBox.text()
        point2 = self.Edit.spinBox_2.text()
        point3 = self.Edit.spinBox_3.text()
        point4 = self.Edit.spinBox_4.text()
        point5 = self.Edit.spinBox_5.text()
        percentage = (int(point5) / int(shoots)) * 100
        percentage = round(percentage, 2)
        note = self.Edit.Note.text()
        if note == "":
            note = "No comment"
        curs.execute("SELECT Count(*) FROM {}".format(buffer.login))
        injck = curs.fetchone()
        row = int(injck[0])
        print(row)
        curs.execute("""INSERT INTO {} (Date_of, shoots, point_2, 
                    point_3, point_4, point_5, PercentageOfHits, Note, ID
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(buffer.login),
                     (date, shoots, point2, point3, point4, point5, percentage, note, row))
        db.commit()
        self.close()


app = QtWidgets.QApplication([])
application = Authorization()
application.show()

sys.exit(app.exec())
