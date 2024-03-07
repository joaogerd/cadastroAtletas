import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QPushButton
from PyQt5.QtCore import QDate

class DatePickerDialog(QWidget):
    """
    A PyQt5 dialog for selecting and adding dates to a list.

    Parameters:
        callback (callable): A callback function to handle the selected dates.

    Usage examples:
    >>> app = QApplication(sys.argv)

    # Define a callback function to handle selected dates
    >>> def handle_dates(selected_dates):
    ...     print("Selected dates:", selected_dates)

    # Create a DatePickerDialog instance with the callback
    >>> date_dialog = DatePickerDialog(handle_dates)
    >>> date_dialog.show()

    # Run the PyQt5 application
    >>> sys.exit(app.exec_())
    """

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.layout.addWidget(self.calendar)

        self.button = QPushButton("Add Dates")
        self.button.clicked.connect(self.add_dates)
        self.layout.addWidget(self.button)

        self.dates = []

        self.calendar.selectionChanged.connect(self.on_selection_changed)

        self.setLayout(self.layout)
        self.setWindowTitle("Date Picker")

    def on_selection_changed(self):
        """
        Handle the selection change in the calendar widget.
        """
        selected_date = self.calendar.selectedDate()
        if selected_date not in self.dates:
            self.dates.append(selected_date)

    def add_dates(self):
        """
        Add the selected dates to the list and call the callback function.
        """
        if self.dates:
            self.dates.sort()  # Sort the dates
            formatted_dates = [date.toString("dd-MM-yyyy") for date in self.dates]
            self.callback(formatted_dates)
        else:
            print("No dates selected.")

