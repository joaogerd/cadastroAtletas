import os
import sys
import subprocess
import tempfile
import fitz  # PyMuPDF

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
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
import logging

from .ConnectDB import ConnectDB  # Import the ConnectDB class if it's in a separate file
from .paths import path
from .camera_application import CameraWindow
from .RegistrationForm import RegistrationForm
from .RegistrationNumber import RegistrationNumber
from .BusinessLogic import BusinessLogic

class cadastroDialog(QtWidgets.QDialog):
    imagePath = None
    IDPath = None
    MedicalCertificatePath = None
    AuthorizationPath = None
    uiFile = 'Formulario_'

    def __init__(self, config, db, formType='insert', record_id=None, parent=None):
        super().__init__(parent)
        self.business_logic = BusinessLogic(db)
        self.config = config
        self.db = db
        self.formType = formType
        self.record_id = record_id

        self.initUI(formType)
        self.setupButtons(record_id)
        self.printer = QPrinter()
        if record_id:
            self.setFieldsData(record_id)

        self.show()

    def setupButtons(self, record_id):
        # Configuração dos botões
        insertUpdateButton = self.findChild(QtWidgets.QPushButton, self.formType)
        insertUpdateButton.clicked.connect(lambda: self.insertOrUpdateButtonPressed(record_id))

        printButton = self.findChild(QtWidgets.QPushButton, 'printButton')
        printButton.clicked.connect(lambda: self.printButtonPressed(record_id))

        closeButton = self.findChild(QtWidgets.QPushButton, 'closeButton')
        closeButton.clicked.connect(self.cancelButtonPressed)

        self.photoButton = self.findChild(QtWidgets.QPushButton, 'foto')
        self.photoButton.clicked.connect(self.selectPhoto)

        self.certButton = self.findChild(QtWidgets.QPushButton, 'atestado_pdf')
        self.certButton.clicked.connect(self._selectMedicalCertificateFromFile)

        self.idButton = self.findChild(QtWidgets.QPushButton, 'rg_pdf')
        self.idButton.clicked.connect(self._selectIDFromFile)

        self.authButton = self.findChild(QtWidgets.QPushButton, 'autorizacao_pdf')
        self.authButton.clicked.connect(self._selectAuthorizationFromFile)



    def initUI(self, formType):
        uiFile = os.path.join(path.ui, self.uiFile + self.formType + '.ui')
        uic.loadUi(uiFile, self)
        self.initializeFieldMappings()

    def initializeFieldMappings(self):
        self.fields = {}
        self.oType = {}

        for name, obj in dict(self.__dict__).items():
            if isinstance(obj, (QtWidgets.QLineEdit, QtWidgets.QDateEdit, 
                                QtWidgets.QRadioButton, QtWidgets.QPushButton, 
                                QtWidgets.QCheckBox)):
                widgetType = obj.__class__.__name__
                self.oType[name] = widgetType
                self.fields[name] = obj

    def insertOrUpdateButtonPressed(self, record_id=None):
        """
        Handle the "Insert" or "Update" button press event.
        """
        isInsert = record_id is None
        fields = self.collectFieldData(isInsert=isInsert)

        if isInsert:
            success = self.business_logic.insert_row(**fields)
        else:
            success = self.business_logic.update_row(record_id, **fields)

        if success:
            logging.info("Data processed successfully.")
        else:
            logging.error("Failed to process data.")

        self.resetFormFields()

        #close dialog
        self.reject()

    def collectFieldData(self, isInsert=False):
        """
        Collect data from the form fields based on the database column keys.
        
        Args:
            isInsert (bool): Flag indicating if this is for an insert operation.
        """
        fields_data = {}
        birth_date_str = None

        for key in self.db.keys:
            if key in self.oType:
                widget_type = self.oType[key]
                widget = self.fields.get(key)
                if widget_type == 'QLineEdit':
                    fields_data[key] = widget.text() if widget else ''
                elif widget_type == 'QDateEdit':
                    date_str = widget.date().toString("dd/MM/yyyy") if widget else None
                    if key == 'dtNascimento':
                        birth_date_str = date_str
                    fields_data[key] = date_str
                elif widget_type == 'QPushButton':
                    if key == 'foto' and self.imagePath:
                        fields_data[key] = self.readImageFile(self.imagePath)
                    elif key == 'rg_pdf' and self.IDPath:
                        print('-----------------------------------------------')
                        fields_data[key] = self.readPDFFile(self.IDPath)
                    elif key == 'atestado_pdf' and self.MedicalCertificatePath:
                        fields_data[key] = self.readPDFFile(self.MedicalCertificatePath)
                    elif key == 'autorizacao_pdf' and self.AuthorizationPath:
                        fields_data[key] = self.readPDFFile(self.AuthorizationPath)
                    else:
                        fields_data[key] = None
                elif widget_type in ['QRadioButton', 'QCheckBox']:
                    fields_data[key] = widget.isChecked() if widget else False

        # Gerar número de matrícula para novos alunos
        if isInsert and birth_date_str:
            birth_year = datetime.strptime(birth_date_str, "%d/%m/%Y").year
            registration = RegistrationNumber(self.db, self.config, birth_year, datetime.now().year)
            fields_data['matricula'] = registration.registration_number

        return fields_data

    def readImageFile(self, imagePath):
        """
        Reads an image file and returns its content in binary format.
        """
        try:
            with open(imagePath, "rb") as file:
                return sqlite3.Binary(file.read())
        except IOError as e:
            logging.error(f"Error reading image file: {e}")
            return None

    def readPDFFile(self, PDFPath):
        """
        Reads a pdf file and returns its content in binary format.
        """
        try:
            with open(PDFPath, "rb") as file:
                return sqlite3.Binary(file.read())
        except IOError as e:
            logging.error(f"Error reading PDF file: {e}")
            return None


    def resetFormFields(self):
        """
        Reset the form fields after insertion or update.
        """
        for key in self.db.keys:
            if key in self.oType:
                widget_type = self.oType[key]
                widget = self.fields.get(key)

                if widget_type == 'QLineEdit':
                    widget.clear()
                elif widget_type == 'QDateEdit':
                    widget.setDateTime(QDateTime(2000, 1, 1, 0, 0))
                elif widget_type == 'QPushButton' and key == 'foto':
                    self.resetPhotoButton()
                elif widget_type in ['QRadioButton', 'QCheckBox']:
                    widget.setChecked(False)

    def resetPhotoButton(self):
        """
        Reset the photo button to its default state.
        """
        self.imagePath = None
        icon_path = os.path.join(path.icon, 'do-utilizador_128.png')
        self.photoButton.setIcon(QIcon(icon_path))
        self.photoButton.setIconSize(QSize(128, 128))
        
    def insertButtonPressed(self):
        """
        Handle the "Insert" button press event.
        """
        fields = self.collectFieldData()
        success = self.business_logic.insert_row(**fields)

        if success:
            logging.info("Data inserted successfully.")
        else:
            logging.error("Failed to insert data.")

        self.resetFormFields()

    def selectPhoto(self):
        """
        Open a dialog to choose between capturing an image or selecting an existing one.
    
        Example:
        >>> self.selectPhoto()
        """
        
        choice, _ = QInputDialog.getItem(
            self, "Choose an option", "Capture or Select?", ["Capture", "Select"], 0, False
        )

        if choice == "Capture":
            self._openCameraWindow()
        elif choice == "Select":
            self._selectImageFromFile()

    def _openCameraWindow(self):
        # Create and show the CameraWindow to capture an image
        self.camera_window = CameraWindow(capture_width_cm=3, capture_height_cm=4, dpi=300)
        self.camera_window.show()
        
        # Connect the imageCaptured signal to the setImageSlot method
        self.camera_window.imageCaptured.connect(self.setImageSlot)

    def _selectImageFromFile(self):
        # Open a file dialog to select an image and set it as the button icon
        file_dialog = QFileDialog()
        self.imagePath, _ = file_dialog.getOpenFileName(self, "Select an image", "", "Image Files (*.png *.jpg *.jpeg)")
    
        # Set the image as the button icon
        if self.imagePath:
            self.photoButton.setIcon(QIcon(self.imagePath))
            self.photoButton.setIconSize(QSize(128, 170))
            self.photoButton.setText('')

    def _selectIDFromFile(self):
        # Open a file dialog to select an ID (Identity Document) file
        options = QFileDialog.Options()
        self.IDPath, _ = QFileDialog.getOpenFileName(self, "Select RG File", "",
                                                  "All Files (*);;PDF Files (*.pdf)", options=options)
        if self.IDPath:
            print(self.IDPath)
    def _selectMedicalCertificateFromFile(self):
        # Open a file dialog to select a medical certificate file
        options = QFileDialog.Options()
        self.MedicalCertificatePath, _ = QFileDialog.getOpenFileName(self, "Select Medical Certificate File", "",
                                                  "All Files (*);;PDF Files (*.pdf)", options=options)

    def _selectAuthorizationFromFile(self):
        # Open a file dialog to select an Authorization file
        options = QFileDialog.Options()
        self.AuthorizationPath, _ = QFileDialog.getOpenFileName(self, "Select Authorization File", "",
                                                  "All Files (*);;PDF Files (*.pdf)", options=options)

    def setImageSlot(self, q_image):
        """
        Set the captured QImage as the button icon and save it temporarily.

        Args:
            q_image (QImage): The captured image.

        Example:
        >>> self.setImageSlot(QImage)
        """

        temp_file = self._saveTempImage(q_image)
        self.imagePath = temp_file
        self._updatePhotoButtonWithImage(q_image)

    def _saveTempImage(self, q_image):
        # Create a temporary directory to save the captured image
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "captured_image.jpg")

        # Save the captured image to the temporary file
        q_image.save(temp_file)

        self.imagePath = temp_file  # Set the temporary file path as self.imagePath

    def _updatePhotoButtonWithImage(self, q_image):
        self.photoButton.setIcon(QIcon(QPixmap.fromImage(q_image)))
        self.photoButton.setIconSize(QSize(128, 170))
        self.photoButton.setText('')

    def cancelButtonPressed(self):
        """
        Handle the "Cancel" button press event to close the application.

        Example:
        >>> self.cancelButtonPressed()
        """
        self.reject()


    def setFieldsData(self, id_value):
        """
        Set the fields' data based on the provided ID.
        """
        data = self.business_logic.fetch_athlete_data(id_value)

        if not data:
            QtWidgets.QMessageBox.warning(self, "Error", "Athlete not found.")
            return

        for key, value in data.items():
            if key in self.oType and value is not None:
                widget = self.fields.get(key)
                widget_type = self.oType[key]

                if widget_type == 'QLineEdit':
                    widget.setText(str(value))
                elif widget_type == 'QDateEdit':
                    date_obj = datetime.strptime(value, "%d/%m/%Y")
                    widget.setDateTime(date_obj)
                elif widget_type == 'QPushButton' and key == 'foto':
                    self.setPhoto(value, widget)
                elif widget_type in ['QRadioButton', 'QCheckBox']:
                    widget.setChecked(bool(value))

    def setPhoto(self, image_data, widget):
        """
        Set the photo in the QPushButton widget.
        """
        try:
            pixmap = QPixmap.fromImage(ImageQt(image_data))
            widget.setIcon(QIcon(pixmap))
            widget.setIconSize(QSize(128, 128))
        except Exception as e:
            logging.error(f"Erro ao abrir a imagem: {e}")

    def form(self, athlete_id, pdf_file_path):

        
        # get athlete data
        atletas_data = self.business_logic.fetch_athlete_data(athlete_id)

        # Create a RegistrationForm instance and generate the PDF
        header_text = f"{self.config.app_config.nome}<br/>"
        header_text += f"{self.config.app_config.rua}, {self.config.app_config.numero}, {self.config.app_config.cidade} - {self.config.app_config.uf}<br/>"
        header_text += f"{self.config.app_config.fone_contato}"

        # create form
        registration_form = RegistrationForm(header_text=header_text,logo=self.config.logo_file, form_filename=pdf_file_path)
        registration_form.create_form(atletas_data)
        registration_form.save_pdf()


    def printButtonPressed(self, athlete_id):

        """Handles the 'Print' button press event to generate a registration form PDF."""

        # Create a temporary file for the PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_file_path = temp_pdf.name

        self.form(athlete_id,pdf_file_path)

        try:
            if sys.platform.startswith('win32'):  # Windows
                subprocess.run(f'start /print "{pdf_file_path}"', shell=True, check=True)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(f'open -a Preview "{pdf_file_path}"', shell=True, check=True)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(f'xdg-open "{pdf_file_path}"', shell=True, check=True)
                #self.print_dialog(pdf_file_path)
            else:
                print("Printing is not supported on this operating system.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to open print dialog: {e}")

        self.getPDFFiles(athlete_id)

    def print_dialog(self, pdf_file_path):
        print_dialog = QPrintDialog(self.printer, self)
    
        # Set up printer and dialog properties
        self.printer.setDocName("My PDF Document")
        self.printer.setOrientation(QPrinter.Orientation.Portrait)
    
        # Execute the print dialog
        if print_dialog.exec_() == QPrintDialog.Accepted:
            try:
                doc = fitz.open(pdf_file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)  # Load the current page
                    pix = page.get_pixmap()  # Render page to a pixmap
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
    
                    painter = QPainter(self.printer)
                    rect = painter.viewport()
                    size = img.size()
                    size.scale(rect.size(), Qt.KeepAspectRatio)
                    painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                    painter.setWindow(img.rect())
                    painter.drawImage(0, 0, img)
                    painter.end()
    
                    if page_num < len(doc) - 1:
                        self.printer.newPage()
    
                doc.close()
                print("Printing completed.")
    
            except Exception as e:
                print(f"An error occurred during printing: {e}")
                # Optionally, show an error message to the user
        else:
            print("Printing canceled by user")

    def printButtonPressed_(self, athlete_id):
        """
        Handles the 'Print' button press event to generate a registration form PDF.
        """
        athlete_data = self.business_logic.fetch_athlete_data(athlete_id)
        if not athlete_data:
            QtWidgets.QMessageBox.warning(self, "Error", "Athlete data not found.")
            return

        header_text = self.generateHeader()
        header_text = f"{self.config.app_config.nome}<br/>"
        header_text += f"{self.config.app_config.rua}, {self.config.app_config.numero}, {self.config.app_config.cidade} - {self.config.app_config.uf}<br/>"
        header_text += f"{self.config.app_config.fone_contato}"

        registration_form = RegistrationForm(header_text=header_text, logo=self.config.logo_file)
        registration_form.create_form(athlete_data)
        registration_form.save_pdf()

    
    def generateHeader(self):
        """
        Generates the header text for the registration form.
        """
        header_parts = [
            f"{self.config.app_config.nome}<br/>",
            f"{self.config.app_config.rua},"
            f"{self.config.app_config.numero},"
            f"{self.config.app_config.cidade} - {self.config.app_config.uf}",
            f"self.config.app_config.fone_contato"
        ]
        return "<br/>".join(header_parts)

    def getPDFFiles(self,athlete_id):

        athlete_data = self.business_logic.fetch_athlete_data(athlete_id)
        if not athlete_data:
            QtWidgets.QMessageBox.warning(self, "Error", "Athlete data not found.")
            return

        for key in ['rg_pdf','atestado_pdf','autorizacao_pdf']:
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            pdf_file_path = temp_pdf.name
           
            with open(pdf_file_path, 'wb') as f:
                f.write(athlete_data[key])
    
            try:
                if sys.platform.startswith('win32'):  # Windows
                    subprocess.run(f'start /print "{pdf_file_path}"', shell=True, check=True)
                elif sys.platform.startswith('darwin'):  # macOS
                    subprocess.run(f'open -a Preview "{pdf_file_path}"', shell=True, check=True)
                elif sys.platform.startswith('linux'):  # Linux
                    subprocess.run(f'xdg-open "{pdf_file_path}"', shell=True, check=True)
                    #self.print_dialog(pdf_file_path)
                else:
                    print("Printing is not supported on this operating system.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to open print dialog: {e}")

