import sys
import os
import configparser
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QFileDialog, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from .paths import path

xpos = 100
ypos = 100
width = 500
height = 70

class AppConfig:
    def __init__(self):
        self.db_file = ""
        self.logo_file = ""
        self.team_name = ""
        self.team_address = ""
        self.team_phone = ""

class AppConfigManager:
    def __init__(self):
        self.config_file = os.path.expanduser("~/.futsalPro/config.ini")

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            app_config = AppConfig()
            app_config.db_file = config.get("AppConfig", "db_file", fallback="")
            app_config.logo_file = config.get("AppConfig", "logo_file", fallback="")
            app_config.team_name = config.get("AppConfig", "team_name", fallback="")
            app_config.team_address = config.get("AppConfig", "team_address", fallback="")
            app_config.team_phone = config.get("AppConfig", "team_phone", fallback="")
            return app_config
        else:
            return AppConfig()

    def save_config(self, app_config):
        config = configparser.ConfigParser()
        config["AppConfig"] = {
            "db_file": app_config.db_file,
            "logo_file": app_config.logo_file,
            "team_name": app_config.team_name,
            "team_address": app_config.team_address,
            "team_phone": app_config.team_phone,
        }

        with open(self.config_file, "w") as cfgfile:
            config.write(cfgfile)

class ConfigDialog(QDialog):
    def __init__(self, app_config):
        super().__init__()
        self.app_config = app_config
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dialog - untitled*")
        self.setGeometry(xpos, ypos, width + 300, height + 200)  # Ajuste o tamanho para acomodar todos os widgets
    
        # Criação do layout do formulário
        formLayout = QFormLayout()
    
        # Configuração do logo
        self.logoLabel = QLabel(self)
        logoPixmap = QPixmap(self.app_config.logo_file)
        self.logoLabel.setPixmap(logoPixmap.scaled(64, 64, Qt.KeepAspectRatio))
        formLayout.addRow("LOGO", self.logoLabel)
    
        # Campo do arquivo de banco de dados com botão de procura
        databaseFileLabel = QLabel("Database File:")
        self.databaseFileInput = QLineEdit(self)
        self.databaseFileInput.setText(self.app_config.db_file)
        databaseBrowseButton = QPushButton("Browse", self)
        databaseBrowseButton.clicked.connect(self.select_database)
        databaseLayout = QHBoxLayout()
        databaseLayout.addWidget(self.databaseFileInput)
        databaseLayout.addWidget(databaseBrowseButton)
        formLayout.addRow(databaseFileLabel, databaseLayout)
    
        # Configuração para o campo de nome da equipe
        teamNameLabel = QLabel("Team Name:")
        self.teamNameInput = QLineEdit(self)
        self.teamNameInput.setText(self.app_config.team_name)
        formLayout.addRow(teamNameLabel, self.teamNameInput)
    
        # Configuração para o campo de endereço da equipe
        teamAddressLabel = QLabel("Team Address:")
        self.teamAddressInput = QLineEdit(self)
        self.teamAddressInput.setText(self.app_config.team_address)
        formLayout.addRow(teamAddressLabel, self.teamAddressInput)
    
        # Configuração para o campo de telefone da equipe
        teamPhoneLabel = QLabel("Team Phone:")
        self.teamPhoneInput = QLineEdit(self)
        self.teamPhoneInput.setText(self.app_config.team_phone)
        formLayout.addRow(teamPhoneLabel, self.teamPhoneInput)
    
        # Botões de salvar e cancelar
        buttonLayout = QHBoxLayout()
        saveButton = QPushButton('OK', self)
        cancelButton = QPushButton('Cancel', self)
        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(cancelButton)
        formLayout.addRow(buttonLayout)
    
        self.setLayout(formLayout)
    
        saveButton.clicked.connect(self.save_config)
        cancelButton.clicked.connect(self.reject)  # Para fechar o diálogo sem salvar
    
        # Ajuste o tamanho dos widgets e alinhamento para combinar com o layout da imagem anexa
        self.adjustSize()

    def select_logo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)

        if file_name:
            self.app_config.logo_file = file_name

    def select_database(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "Database Files (*.db);;All Files (*)", options=options)

        if file_name:
            self.app_config.db_file = file_name

    def save_config(self):
        self.app_config.team_name = self.teamNameInput.text()
        self.app_config.team_address = self.teamAddressInput.text()
        self.app_config.team_phone = self.teamPhoneInput.text()
        app_config_manager.save_config(self.app_config)
        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app_config_manager = AppConfigManager()
    app_config = app_config_manager.load_config()

    if not app_config.logo_file:
        app_config.logo_file = os.path.join(path.logos, 'futsalPro_logo.png')
    if not app_config.db_file:
        app_config.db_file = os.path.expanduser("~/.futsalPro/atletas.db")

    ex = ConfigDialog(app_config)
    ex.exec_()

    sys.exit(app.exec_())

