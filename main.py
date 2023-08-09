from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, \
     QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog,\
     QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import os
import mysql.connector


class DatabaseConnection:

    def __init__(self, host="localhost", user="root",
                 password=os.getenv("MySQL password"), database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)
        main_grid = QGridLayout()

        # Create menu bar options
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Create Add Student option for the File menu list
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Create an Exit option for the File menu list
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_program)
        file_menu_item.addAction(exit_action)

        # Create an About action item for the Help menu list
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)


        search_action = QAction(QIcon('icons/search.png'), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        # Create and insert the data table into the window
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        # Add actions to the toolbar
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        insert_dialog = InsertDialog()
        insert_dialog.exec()

    def search(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def exit_program(self):
        exit()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during as part of the Python Mega Course.
        Feel free to modify and reuse this app as you see fit.
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setText(student_name)
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile_number = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit()
        self.mobile.setText(mobile_number)
        layout.addWidget(self.mobile)

        # Add submit button
        submit_button = QPushButton("Update")
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.update_student)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        main_window.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()

        # Add "are you sure?" message
        self.confirmation = QLabel("Are you sure you want to delete this record?")
        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")

        layout.addWidget(self.confirmation, 0, 0, 1, 2)
        layout.addWidget(self.yes_button, 1, 0)
        layout.addWidget(self.no_button, 1, 1)

        self.setLayout(layout)

        self.yes_button.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get index and student ID for selected row
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Confirmation")
        confirmation_widget.setText("Record successfully deleted")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Add Mobile Number")
        layout.addWidget(self.mobile)

        # Add submit button
        submit_button = QPushButton("Submit")
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student Records")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add the search box
        self.search_term = QLineEdit()
        self.search_term.setPlaceholderText("What are you looking for?")
        layout.addWidget(self.search_term)

        # Add the search button
        search_button = QPushButton("Search")
        layout.addWidget(search_button)
        search_button.clicked.connect(self.search)

        self.setLayout(layout)

    def search(self):
        name = self.search_term.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
