import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
from qtwidgets import Toggle, AnimatedToggle

from .AppConfigManager import AppConfigManager
from .paths import path

class AppConfigDialog(QtWidgets.QDialog):
    """A dialog for managing application configuration settings.

    This class provides a user interface for configuring various application settings,
    including the database file, address, contact information, and logo selection.

    Attributes:
        config_saved (QtCore.pyqtSignal): A custom signal emitted when configuration is saved.

    Methods:
        __init__(self, parent=None): Initializes the AppConfigDialog.
        setupUi(self): Sets up the user interface elements.
        connectSignals(self): Connects signals to their respective slots.
        selectLogo(self): Opens a file dialog to select a logo image file.
        selectDatabase(self): Opens a file dialog to select a database file.
        acceptConfiguration(self): Handles the "Save" action.
        rejectConfiguration(self): Handles the "Cancel" action.
        loadConfiguration(self): Loads the existing configuration.
        openConfigurationDialog(self): Opens the configuration dialog for updating settings.
        updateUI(self): Updates the user interface with the current configuration.
        updateLogo(self, file_name): Updates the logo display.
        updateDatabaseFile(self, file_name): Updates the database file display.
        saveConfiguration(self): Saves the current configuration settings.
        getDatabaseFile(self): Gets the selected database file.
        getNome(self): Gets the configured name.
        getRua(self): Gets the configured street address.
        getNumero(self): Gets the configured street number.
        getCidade(self): Gets the configured city.
        getUf(self): Gets the configured state or province.
        getCep(self): Gets the configured postal code.
        getFoneContato(self): Gets the configured contact phone number.
        getDtNascimento(self): Gets the configured date of birth.
        getDocCpf(self): Gets the configured CPF (Brazilian tax ID).
        getEmailResponsavel(self): Gets the configured responsible person's email address.

    Example:
        # Create an instance of AppConfigDialog
        config_dialog = AppConfigDialog()

        # Open the configuration dialog and populate it with existing settings
        config_dialog.openConfigurationDialog()

        # Execute the dialog and handle the signals emitted upon save or cancel
        result = config_dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            # Configuration is saved
            print("Configuration saved.")
        else:
            # Configuration is canceled or rejected
            print("Configuration canceled.")
    """

    config_saved = pyqtSignal()  # Custom signal to indicate that configuration is saved

    def __init__(self, parent=None):
        """Initialize the AppConfigDialog.

        Args:
            parent (QWidget): The parent widget.
        """
        super(AppConfigDialog, self).__init__(parent)
        self.setupUi()
        self.connectSignals()
        self.loadConfiguration()


    def setupToggle(self):
        """include toggle button to category even"""
        self.category_even = Toggle()
        self.toggleContainer = self.findChild(QtWidgets.QWidget, 'toggleContainer')
        self.toggleContainer.setLayout(QtWidgets.QVBoxLayout())
        self.toggleContainer.layout().addWidget(self.category_even)        

    def setupUi(self):
        """Sets up the user interface elements."""
        uiFile = os.path.join(path.ui, "appConfig.ui")
        uic.loadUi(uiFile, self)
        self.setWindowTitle("Configurações")
        self.logo_file = ""
        self.config_manager = AppConfigManager()
        self.setupToggle()

    def connectSignals(self):
        """Connects signals to their respective slots."""
        self.browseButton.clicked.connect(self.selectDatabase)
        self.browseButton_table.clicked.connect(self.selectDatabaseTable)
        self.logo.clicked.connect(self.selectLogo)
        self.buttonBox.accepted.connect(self.acceptConfiguration)
        self.buttonBox.rejected.connect(self.rejectConfiguration)

    def selectLogo(self):
        """Opens a file dialog to select a logo image file."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Logo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
            options=options
        )
        if file_name:
            self.updateLogo(file_name)

    def selectDatabase(self):
        """Opens a file dialog to select a database file."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Database File", "", "Database Files (*.db);;All Files (*)", options=options
        )
        if file_name:
            self.updateDatabaseFile(file_name)

    def selectDatabaseTable(self):
        """Opens a file dialog to select a database file."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Database Table File", "", "Database Tables Files (*.sql);;All Files (*)", options=options
        )
        if file_name:
            self.updateDatabaseTableFile(file_name)

    def acceptConfiguration(self):
        """Handles the 'Save' action."""
        reply = QMessageBox.question(
            self, "Salvar Configurações",
            "Deseja salvar as alterações?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            self.saveConfiguration()
            self.config_saved.emit()
            super().accept()
        elif reply == QMessageBox.No:
            super().accept()
        else:
            pass  # Cancel, do nothing

    def rejectConfiguration(self):
        """Handles the 'Cancel' action."""
        reply = QMessageBox.question(
            self, "Descartar Alterações",
            "As modificações serão perdidas. Deseja continuar?",
            QMessageBox.Ok | QMessageBox.Cancel
        )

        if reply == QMessageBox.Ok:
            super().reject()
        else:
            pass  # Cancel, do nothing

    def loadConfiguration(self):
        """Loads the existing configuration."""
        self.app_config,config_exists = self.config_manager.loadConfig()
        self.updateUI()
        if not config_exists:
            self.openConfigurationDialog()

    def openConfigurationDialog(self):
        """Opens the configuration dialog for updating settings."""
        self.exec_()
        self.updateUI()

    def updateUI(self):
        """Updates the user interface with the current configuration."""
        self.dataBaseFile.setText(self.app_config.database_file)
        self.dataBaseFile_table_file.setText(self.app_config.database_table_file)
        self.dataBaseFile_table_name.setText(self.app_config.database_table_name)
        self.nome.setText(self.app_config.nome)
        self.rua.setText(self.app_config.rua)
        self.numero.setText(self.app_config.numero)
        self.cidade.setText(self.app_config.cidade)
        self.UF.setText(self.app_config.uf)
        self.CEP.setText(self.app_config.cep)
        self.foneContato.setText(self.app_config.fone_contato)
        self.dtFundacao.setDate(QDate.fromString(self.app_config.dt_fundacao, "dd/MM/yyyy"))
        self.CNPJ.setText(self.app_config.cnpj)
        self.emailContato.setText(self.app_config.email_contato)
        self.updateLogo(self.app_config.logo_file)
        self.category_even.setChecked(self.app_config.categoria_par == "True")

    def updateLogo(self, file_name):
        """Updates the logo display."""
        self.logo.setIcon(QIcon(file_name))
        self.logo.setIconSize(QSize(128, 128))
        self.logo.setText("")  # Remove the text "LOGO" from the button
        self.logo_file = file_name

    def updateDatabaseFile(self, file_name):
        """Updates the database file display."""
        self.dataBaseFile.setText(file_name)

    def updateDatabaseTableFile(self, file_name):
        """Updates the database file display."""
        self.dataBaseTableFile.setText(file_name)

    def saveConfiguration(self):
        """Saves the current configuration settings."""
        self.app_config.database_file = self.getDatabaseFile()
        self.app_config.database_table_file = self.getDatabaseTableFile()
        self.app_config.database_table_name = self.getDatabaseTableName()
        self.app_config.nome = self.getNome()
        self.app_config.rua = self.getRua()
        self.app_config.numero = self.getNumero()
        self.app_config.cidade = self.getCidade()
        self.app_config.uf = self.getUf()
        self.app_config.cep = self.getCep()
        self.app_config.cnpj = self.getCNPJ()
        self.app_config.dt_fundacao = self.getDtFundacao()
        self.app_config.fone_contato = self.getFoneContato()
        self.app_config.email_contato = self.getEmailContato()
        self.app_config.logo_file = self.logo_file
        self.app_config.categoria_par = self.getCategoryType()

        self.config_manager.saveConfig(self.app_config)
        self.updateUI()

    def getDatabaseFile(self):
        """Gets the selected database file."""
        return self.dataBaseFile.text()

    def getDatabaseTableFile(self):
        """Gets the selected database table config file."""
        return self.dataBaseFile_table_file.text()

    def getDatabaseTableName(self):
        """Gets the selected database table name."""
        return self.dataBaseFile_table_name.text()

    def getNome(self):
        """Gets the configured name."""
        return self.nome.text()

    def getRua(self):
        """Gets the configured street address."""
        return self.rua.text()

    def getNumero(self):
        """Gets the configured street number."""
        return self.numero.text()

    def getCidade(self):
        """Gets the configured city."""
        return self.cidade.text()

    def getUf(self):
        """Gets the configured state or province."""
        return self.UF.text()

    def getCep(self):
        """Gets the configured postal code."""
        return self.CEP.text()

    def getFoneContato(self):
        """Gets the configured contact phone number."""
        return self.foneContato.text()

    def getDtFundacao(self):
        """Gets the configured date of birth."""
        return self.dtFundacao.date().toString("dd/MM/yyyy")

    def getCNPJ(self):
        """Gets the configured CPF (Brazilian tax ID)."""
        return self.CNPJ.text()

    def getEmailContato(self):
        """Gets the configured responsible person's email address."""
        return self.emailContato.text()

    def getCategoryType(self):
        """Gets the configured category type."""
        return self.category_even.isChecked()

