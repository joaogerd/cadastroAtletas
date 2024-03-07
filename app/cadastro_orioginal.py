import os
import sys
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import QDateTime, QSize, QObject
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QFileDialog, QMessageBox, QPushButton, QInputDialog
import sqlite3
import pandas as pd
from datetime import datetime, date
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt
import tempfile

from .ConnectDB import ConnectDB  # Import the ConnectDB class if it's in a separate file
from .paths import path
from .camera_application import CameraWindow
from .RegistrationForm import RegistrationForm
from .RegistrationNumber import RegistrationNumber

#from .AppConfigDialog import AppConfigDialog

# Obtém os argumentos passados pelo view.py
#args = sys.argv[1:]

class cadastroDialog(QtWidgets.QDialog):
    """
    A PyQt-based UI class for interacting with an SQLite database.

    Attributes:
        imagePath (str): The path to the selected image.

    Methods:
        __init__(self, args): Initializes the UI and connects to the database.
        selectPhoto(self): Opens a file dialog to select an image.
        setFieldsData(self, id_value): Sets the fields' data based on the provided ID.
        insertButtonPressed(self): Handles the "Insert" button press event.
        update_row(self, row_id, **kwargs): Updates a row in the database.
        printButtonPressed(self): Handles the "Print" button press event.
        cancelButtonPressed(self): Handles the "Cancel" button press event.
        initUI(self): Initializes the UI by loading the .ui file and obtaining field objects.
    """

    imagePath = ''
    uiFile    = 'Formulario_'

    def __init__(self, config, db, formType='insert',record_id=None, parent=None):
        """
        Initialize the UI and connect to the database.

        Args:
            args: Additional command-line arguments.

        Example:
        >>> app = QtWidgets.QApplication(sys.argv)
        >>> window = Ui(args)
        >>> app.exec_()
        """
        super(cadastroDialog, self).__init__(parent)
        self.config = config

        # Connect to the database
        self.db  =  db

        # Create the UI
        self.initUI(formType)

        # Set up buttons
        self.button = self.findChild(QtWidgets.QPushButton, formType)
        self.button.clicked.connect(lambda: self.insertOrUpdateButtonPressed(record_id))

        self.button = self.findChild(QtWidgets.QPushButton, 'printButton')
        self.button.clicked.connect(lambda: self.printButtonPressed(record_id))

        self.button = self.findChild(QtWidgets.QPushButton, 'closeButton')
        self.button.clicked.connect(self.cancelButtonPressed)

        self.photoButton = self.findChild(QtWidgets.QPushButton, 'foto')
        self.photoButton.clicked.connect(self.selectPhoto)

        # Show the app
        self.show()

        if record_id:
            self.setFieldsData(record_id)

    def selectPhoto(self):
        """
        Open a dialog to choose between capturing an image or selecting an existing one.
    
        Example:
        >>> self.selectPhoto()
        """
        options = ["Capture", "Select"]
        choice, _ = QInputDialog.getItem(self, "Choose an option", "Capture or Select?", options, 0, False)
    
        if choice == "Capture":
            # Create and show the CameraWindow to capture an image
            self.camera_window = CameraWindow(capture_width_cm=3, capture_height_cm=4, dpi=300)
            self.camera_window.show()
    
            # Connect the imageCaptured signal to the setImageSlot method
            self.camera_window.imageCaptured.connect(self.setImageSlot)
        elif choice == "Select":
            # Open a file dialog to select an image and set it as the button icon
            file_dialog = QFileDialog()
            self.imagePath, _ = file_dialog.getOpenFileName(self, "Select an image", "", "Image Files (*.png *.jpg *.jpeg)")
    
            # Set the image as the button icon
            if self.imagePath:
                self.photoButton.setIcon(QIcon(self.imagePath))
                self.photoButton.setIconSize(QSize(128, 170))
                self.photoButton.setText('')
    
    def setImageSlot(self, q_image):
        """
        Set the captured QImage as the button icon and save it temporarily.

        Args:
            q_image (QImage): The captured image.

        Example:
        >>> self.setImageSlot(QImage)
        """
        # Create a temporary directory to save the captured image
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "captured_image.jpg")

        # Save the captured image to the temporary file
        q_image.save(temp_file)

        self.imagePath = temp_file  # Set the temporary file path as self.imagePath

        self.photoButton.setIcon(QIcon(QPixmap.fromImage(q_image)))
        self.photoButton.setIconSize(QSize(128, 170))
        self.photoButton.setText('')

    def setFieldsData(self, id_value):
        """
        Set the fields' data based on the provided ID.
    
        Args:
            id_value (int): The ID of the record to retrieve and populate the fields with.
    
        Example:
        >>> self.setFieldsData(1)
        """

        data = self.db.readById(id_value)
    
        if data:
            fields = {}
            for k, value in zip(self.db.keys, data[1:]):
                oType = self.oType[k]
                if value:
                    value_type = type(value)
                    print(f"O tipo de 'value' é: {value_type}, {k}")
                    if oType == 'QDateEdit':
                        fields[k] = datetime.strptime(value, "%d/%m/%Y")
                    elif oType == 'QPushButton' and k == 'foto':
                        try:
                            image = Image.open(BytesIO(value))
                            pixmap = QPixmap.fromImage(ImageQt(image))
                            fields[k] = pixmap
                        except Exception as e:
                            print(f"Erro ao abrir a imagem: {e}")
                    elif oType == 'QRadioButton':
                        fields[k] = bool(value)
                    elif oType == 'QCheckBox':
                        fields[k] = bool(value)
                    else:
                        fields[k] = str(value)
    
            for k, Field in self.fields.items():
                if k in fields:
                    oType = self.oType[k]
    
                    if oType == 'QDateEdit':
                        Field.setDateTime(fields[k])
                    elif oType == 'QPushButton' and k == 'foto':
                        if isinstance(fields[k], QPixmap):
                            Field.setIcon(QIcon(fields[k]))
                            Field.setIconSize(QSize(128, 128))
                    elif oType == 'QRadioButton':
                        Field.setChecked(fields[k])
                    elif oType == 'QCheckBox':
                        Field.setChecked(fields[k])
                    else:
                        Field.setText(fields[k])
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Athlete not found.")

    def insertButtonPressed(self):
        """
        Handle the "Insert" button press event by inserting data into the database.

        Example:
        >>> self.insertButtonPressed()
        """

        cursor = self.db.conn.cursor()

        insert = f"INSERT INTO {self.db.tbName} ({', '.join(self.db.keys)})"
        insert += "\nVALUES ({})".format(", ".join(["?" for _ in self.db.keys]))

        fields = []
        for k in self.db.keys:
            oType = self.oType[k]
            if oType == 'QDateEdit':
                dateStr = self.fields[k].text()
                fields.append(dateStr)
            elif oType == 'QPushButton':
                if self.imagePath:
                    with open(self.imagePath, "rb") as file:
                        image = file.read()
                        fields.append(sqlite3.Binary(image))
                else:
                    fields.append('')
            elif oType == 'QRadioButton':
                # Handle radio buttons for gender
                if k == 'masculino':
                    fields.append(self.fields[k].isChecked())
                elif k == 'feminino':
                    fields.append(self.fields[k].isChecked())                
            elif oType == 'QCheckBox':
                fields.append(self.fields[k].isChecked())
            else:
                fields.append(self.fields[k].text())

        try:
            cursor.execute(insert.replace("'", ""), tuple(fields))
            self.db.commit_db()
            print("Data inserted successfully.")
        except sqlite3.IntegrityError:
            print(f"Warning: {str(e)}.")
            return False

        for k in self.db.keys:
            oType = self.oType[k]

            if oType == 'QDateEdit':
                self.fields[k].setDateTime(QDateTime(2000, 1, 1, 0, 0))
            elif oType == 'QPushButton':
                self.imagePath = ''
                icon = os.path.join(path.ui, 'do-utilizador_128.png')
                self.photoButton.setIcon(QIcon(icon))
                self.photoButton.setIconSize(QSize(128, 128))
            elif oType == 'QRadioButton': 
                self.fields[k].setChecked(False)
            elif oType == 'QCheckBox':
                self.fields[k].setChecked(False)
            else:
                self.fields[k].clear()

    def insertOrUpdateButtonPressed(self, record_id=None):
        """
        Handle the "Insert" or "Update" button press event by inserting or updating data in the database.
    
        Args:
            record_id (int, optional): The unique identifier of the record to update (None for insertion).
    
        Example for insertion:
        >>> self.insertOrUpdateButtonPressed()
    
        Example for updating an existing record with record_id=1:
        >>> self.insertOrUpdateButtonPressed(1)
        """
        
        fields = {}
        for k in self.db.keys:
            oType = self.oType[k]
            if oType == 'QDateEdit':
                dateStr = self.fields[k].text()
                fields[k] = dateStr
            elif oType == 'QPushButton':
                if self.imagePath:
                    with open(self.imagePath, "rb") as file:
                        image = file.read()
                        fields[k] = sqlite3.Binary(image)
                else:
                    fields[k] = None  # Set it to None if imagePath is empty
            elif oType == 'QRadioButton':
                # Handle radio buttons for gender
                fields[k] = self.fields[k].isChecked()
            elif oType == 'QCheckBox':
                fields[k] = self.fields[k].isChecked()
            else:
                fields[k] = self.fields[k].text()
    
        if record_id is None:
            try:
                self.insert_row(**fields)  # Call the generic insert_row method with the dictionary values
                print("Data inserted successfully.")
            except sqlite3.IntegrityError as e:
                print(f"Error: {str(e)}")
                return False
        else:
            try:
                self.update_row(record_id, **fields)  # Call the generic update_row method with the dictionary values
                print("Data updated successfully.")
            except sqlite3.IntegrityError as e:
                print(f"Error: {str(e)}")
                return False
    
        for k in self.db.keys:
            oType = self.oType[k]
    
            if oType == 'QDateEdit':
                self.fields[k].setDateTime(QDateTime(2000, 1, 1, 0, 0))
            elif oType == 'QPushButton':
                self.imagePath = ''
                icon = os.path.join(path.icon, 'do-utilizador_128.png')
                self.photoButton.setIcon(QIcon(icon))
                self.photoButton.setIconSize(QSize(128, 128))
            elif oType == 'QRadioButton': 
                self.fields[k].setChecked(False)
            elif oType == 'QCheckBox':
                self.fields[k].setChecked(False)
            else:
                self.fields[k].clear()

    def insert_row(self, **kwargs):
        """
        Insert a new row into the database with the provided values.
    
        Args:
            **kwargs: Keyword arguments with column names and their values for insertion.
    
        Returns:
            bool: True if the insertion was successful, False otherwise.
    
        Example:
            >>> self.insert_row(nome='John', email='john@example.com', idade=30)
    
        Raises:
            sqlite3.IntegrityError: If there's a violation of integrity constraints (e.g., unique constraint).
        """
        columns = ','.join(kwargs.keys())
        values = tuple(kwargs.values())
    
        placeholders = ','.join(['?' for _ in kwargs])
    
        query = f"INSERT INTO {self.db.tbName} ({columns}) VALUES ({placeholders})"
        
        try:
            self.db.cursor.execute(query, values)
            self.db.commit_db()
            print("Data inserted successfully.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error: {str(e)}")
            return False


    def update_row(self, row_id, **kwargs):
        """
        Update a row in the database with the provided values.
    
        Args:
            row_id (int): The ID of the row to update.
            **kwargs: Keyword arguments with column names and their new values.
    
        Returns:
            bool: True if the update was successful, False otherwise.
    
        Example:
            >>> self.update_row(1, nome='New Name', email='newemail@example.com')
        """
        # Extract columns and values from kwargs, ignoring columns with None values
        columns = ','.join([f"{col} = ?" for col in kwargs.keys() if kwargs[col] is not None])
        values = [kwargs[col] for col in kwargs.keys() if kwargs[col] is not None]
        values += [row_id]
    
        if not columns:
            print("Error: No columns provided for update.")
            return False
    
        query = f"UPDATE {self.db.tbName} SET {columns} WHERE id = ?"
    
        try:
            self.db.cursor.execute(query, values)
            self.db.commit_db()
            print("Data updated successfully.")
            return True
        except sqlite3.IntegrityError:
            print("Error: {str(e)}.")
            return False


    def printButtonPressed(self, athlete_id):

        """Handles the 'Print' button press event to generate a registration form PDF."""
        #athlete_id = self.get_selected_athlete_id()  # Ensure this method exists and gets the athlete's ID
        atletas_data = self.fetch_athlete_data(athlete_id)
        #print(atletas_data)
        # Create a RegistrationForm instance and generate the PDF
        header_text = f"{self.config.app_config.nome}<br/>"
        header_text += f"{self.config.app_config.rua}, {self.config.app_config.numero}, {self.config.app_config.cidade} - {self.config.app_config.uf}<br/>"
        header_text += f"{self.config.app_config.fone_contato}"
        registration_form = RegistrationForm(header_text=header_text,logo=self.config.logo_file)
        registration_form.create_form(atletas_data)
        registration_form.create_form(atletas_data)
        registration_form.save_pdf()

    def cancelButtonPressed(self):
        """
        Handle the "Cancel" button press event to close the application.

        Example:
        >>> self.cancelButtonPressed()
        """
        print('Close button pressed')
        self.reject()

    def initUI(self, formType):
        """
        Initialize the user interface by loading the .ui file and obtaining field objects.
    
        Args:
            formType (str): The type of form to load (e.g., 'insert' or 'update').
    
        Example:
        >>> self.initUI('insert')
        """
        # Determine the .ui file path based on formType
        uiFile = os.path.join(path.ui, self.uiFile + formType + '.ui')
        
        # Load the .ui file
        uic.loadUi(uiFile, self)
    
        fields = {}
        oType = {}
    
        for name, obj in dict(self.__dict__).items():
            try:
                Type = str(obj).split('.')[2].split(" ")[0]
                if Type in ['QLineEdit', 'QDateEdit', 'QRadioButton', 'QPushButton', 'QCheckBox']:
                    oType[name] = Type
                    fields[name] = obj
    
                    # Obter o objectName do widget
                    #object_name = obj.objectName()
                    #print(f"Widget: {name}, Type: {Type}, Object Name: {object_name}")
    
            except:
                pass
            if not isinstance(obj, QObject):
                continue
    
        self.fields = fields
        self.oType = oType

    def fetch_athlete_data(self, athlete_id):
        """Fetches athlete data from the database given an athlete ID.

        Args:
            athlete_id (int): The ID of the athlete to fetch data for.

        Returns:
            dict: A dictionary containing the athlete's data.
        """
        data = self.db.readById(athlete_id)
        if data:
            athlete_data = {}
            for k, value in zip(self.db.keys, data[1:]):  # Assuming self.db.keys are the column names
                if value is not None:
                    if k == 'foto':
                        try:
                            image = Image.open(BytesIO(value))
                            athlete_data[k] = image  # Storing the image object directly
                        except Exception as e:
                            print(f"Erro ao abrir a imagem: {e}")
                            athlete_data[k] = None
                    elif isinstance(value, datetime):
                        athlete_data[k] = value.strftime("%d/%m/%Y")
                    else:
                        athlete_data[k] = value
            return athlete_data
        else:
            return {}  # Return an empty dictionary if no data is found


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui(args)
    app.exec_()

