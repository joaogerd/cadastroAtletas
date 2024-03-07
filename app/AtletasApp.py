import sys
import os
import json
import configparser
import subprocess
import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QAction,
    QHBoxLayout, QMessageBox, QFileDialog, QApplication, QSizePolicy, QAbstractItemView,
    QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QSize

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from datetime import datetime

import pandas as pd
import numpy as np

from .SplashScreen import SplashScreen
from .DatePickerDialog import DatePickerDialog
from .AtletasTableWidget import AtletasTableWidget
from .PopupWindow import PopupWindow
from .utils import calculate_age_category, age, getCat
from .AppConfigManager import AppConfigManager
from .AppConfigDialog import AppConfigDialog
from .cadastro import cadastroDialog
from .ConnectDB import ConnectDB  # Import the ConnectDB class if it's in a separate file
from .paths import path


   
class AtletasApp(QMainWindow):
    """
    A PyQt5 application for athlete registration with configuration settings.

    This application allows users to manage athlete records and provides the ability to configure
    settings such as the database file name, logo path, and team information. Configuration settings
    are stored in a JSON file located in the user's home directory.

    Attributes:
        teamInfoLabel (QLabel): A QLabel widget to display team information.

    Methods:
        loadConfiguration(): Load configuration settings from the configuration file.
        configureApp(): Open a configuration dialog to set application settings.
    
    Usage:
    - Create an instance of AtletasApp to launch the application:

    >>> app = QApplication(sys.argv)
    >>> atletas_app = AtletasApp()
    >>> atletas_app.show()
    >>> sys.exit(app.exec_())

    - The application will load configuration settings at startup. Users can configure the application
      using the "Configurar" button in the UI.
    - Configuration settings include the database file name, logo path, and team information.

    Examples:
    - Create an instance of AtletasApp:

    >>> app = QApplication([])
    >>> atletas_app = AtletasApp()
    >>> atletas_app.show()
    """
    uiFile    = 'Formulario.ui'

    def __init__(self):
        super(AtletasApp,self).__init__()

        self.config = AppConfigDialog()

        self.layout()

        # Connect the custom signal to the slot for layout update
        #self.config.config_saved.connect(self.update_layout)     

        self.create_db()

        self.create_menus()
        self.create_search_bar()
        self.create_table()
        self.create_buttons()

        #load data inside table view
        self.loadData()

        self.w = []
        #self.preSumula()

        # Connect the custom signal to the slot for layout update
        self.config.config_saved.connect(self.update_layout)

        self.cadastro = None
        
    def layout(self):
        """
        Create the layout for the main window.
    
        This method sets up the layout for the main window, including the logo, text, and other components.
    
        Usage:
        - Automatically called during the initialization of the main window.
        """
        self.setWindowTitle("FutsalPro - Cadastro de Atletas")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.logoTextLayout = QHBoxLayout()
        self.mainLayout = QVBoxLayout(self.centralwidget)
        
        self.create_logo_label()
        self.create_text_label()
        
        self.mainLayout.addLayout(self.logoTextLayout)

        self.update_layout()  # Call the update_layout method to set initial values   
    
    def create_logo_label(self):
        """
        Create the logo label.
    
        This method creates the QLabel widget for displaying the logo.
    
        Usage:
        - Called during the initialization of the layout.
        """
        self.logoLabel = QLabel(self.centralwidget)
        self.logoTextLayout.addWidget(self.logoLabel, 0)  # Set stretch factor to 0 for logoLabel
    
    def create_text_label(self):
        """
        Create the text label.
    
        This method creates the QLabel widget for displaying text information.
    
        Usage:
        - Called during the initialization of the layout.
        """
        self.textLabel = QLabel(self.centralwidget)
        self.logoTextLayout.addWidget(self.textLabel, 1)  # Set stretch factor to 1 for textLabel
    
    def update_layout(self):
        """
        Update the layout with logo and text.
    
        This method updates the logo and text labels with current configuration values.
    
        Usage:
        - Called to update the layout with new configuration values.
        """
        
        # Update logo
        self.update_logo()
        
        # Update text
        self.update_text()

        # Clear tab_widget
        #self.tab_widget.clear()

        # reload data with inserted new data
        #self.loadData()

    def update_logo(self):
        """
        Update the logo label.
    
        This method updates the logo label with the current logo file path from the configuration.
    
        Usage:
        - Called by update_layout.
        """
        pixmap = QPixmap(self.config.app_config.logo_file)  # Use the logo file path from the configuration
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.logoLabel.setPixmap(pixmap)
    
    def update_text(self):
        """
        Update the text label.
    
        This method updates the text label with information from the configuration dialog.
    
        Usage:
        - Called by update_layout.
        """
        text = f"<html><body><h1>{self.config.app_config.nome}</h1><p><h2>{self.config.app_config.rua}, {self.config.app_config.numero}, {self.config.app_config.cidade} - {self.config.app_config.uf}</p><p>{self.config.app_config.fone_contato}</p></body></html>"
        self.textLabel.setText(text)
        self.textLabel.setFont(QFont("Arial", 12))
    
        # Trigger repaint
        self.textLabel.update()
        self.logoLabel.update()
        
    def open_cadastro_atletas(self):
        """
        Open the athlete registration window.

        This method is triggered when the "Cadastrar" button is clicked. It opens a separate window for
        registering new athletes.
        """

        #subprocess.run(["python", "cadastro.py"])
        self.cadastro = cadastroDialog(self.config, self.db)
        self.cadastro.exec_()
        
        # Clear tab_widget
        self.tab_widget.clear()

        # reload data with inserted new data
        self.loadData()

    def create_db(self):

        self.db = ConnectDB(self.config.app_config.database_file)
        self.db.createTable(self.config.app_config.database_table_name)

    def create_table(self):
        """
        Create the main table widget.

        This method creates a QTabWidget to display athlete data in multiple tabs categorized by age groups.
        """

        #
        # Create Table
        #

        self.tab_widget = QTabWidget(self.centralWidget())
        self.tab_widget.setFixedSize(800, 600)
        self.mainLayout.addWidget(self.tab_widget)

    def create_search_bar(self):
        """
        Create the search bar.

        This method creates a search bar for filtering athlete records based on user input.
        """


        search_line = QLineEdit(self)
        search_line.setPlaceholderText("Buscar...")
        search_line.textChanged.connect(self.search_table)

        # Criar um layout Horizontal

        searchLayout = QHBoxLayout()
        #searchLayout.addStretch(1)  # Add stretchable space to push the buttons to the right
        searchLayout.addWidget(search_line)
        searchLayout.addStretch(0)  # Add stretchable space to push the buttons to the right
        searchLayout.addStretch(0)  # Add stretchable space to push the buttons to the right


        self.mainLayout.addLayout(searchLayout)


    def create_buttons(self):
        """
        Create buttons for actions.

        This method creates buttons for common actions such as opening the registration window and closing the application.
        """

        # Abrir cadastro de atletas
        button_cadastro_atletas = QPushButton("Cadastrar", self)
        button_cadastro_atletas.clicked.connect(self.open_cadastro_atletas)
        button_cadastro_atletas.setMaximumWidth(100) # Set the maximum width of the button
        button_cadastro_atletas.setIcon(QIcon(os.path.join(path.icon,'associese-azul_128x128.png')))
        # botào fechar        
        exit_action = QPushButton("Fechar", self)
        exit_action.clicked.connect(self.close)
        exit_action.setMaximumWidth(80)  # Set the maximum width of the button
        exit_action.setIcon(QIcon(os.path.join(path.icon,'sair-azul_128x128.png')))

        # Criar um layout Horizontal

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)  # Add stretchable space to push the buttons to the right

        buttonsLayout.addWidget(button_cadastro_atletas)
        buttonsLayout.addWidget(exit_action)

        
        # Definir o layout como layout principal da janela
        self.mainLayout.addLayout(buttonsLayout)

    def create_actions(self):
        """
        Create actions for menu items.

        This method defines actions that can be performed from the application's menu.
        """

        self.delete_row_action = QAction("Deletar Linha", self)
        self.delete_row_action.triggered.connect(self.delete_selected_row)

        self.select_column_action = QAction("Selecionar Coluna", self)
        self.select_column_action.triggered.connect(self.select_column)

        self.sort_column_action = QAction("Ordenar Coluna", self)
        self.sort_column_action.triggered.connect(self.sort_column)

        self.exit_action = QAction("Fechar", self)
        self.exit_action.triggered.connect(self.close)

    def update(self):
        """
        Update athlete data.

        This method updates the athlete data and refreshes the table view.
        """

        self.w.append(PopupWindow(self))
        self.w[-1].show()


    def create_menus(self):
        """
        Create menus for the application.

        This method creates menus and adds actions to them for various functionalities.
        """

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Arquivo")

        print_action = QAction("Gerar Lista de Presença", self)
        print_action.triggered.connect(self.open_date_picker_dialog)
        icon = os.path.join(path.icon, 'agenda-azul_128x128.png')
        print_action.setIcon(QIcon(icon))

        sort_column = QAction("Ordenar Coluna", self)
        sort_column.triggered.connect(self.sort_column)
        icon = os.path.join(path.icon, 'sort-azul_128x128.png')
        sort_column.setIcon(QIcon(icon))

        delete_row = QAction("Deletar Linha", self)
        delete_row.triggered.connect(self.delete_selected_row)
        icon = os.path.join(path.icon, 'delete-row-128.ico')
        delete_row.setIcon(QIcon(icon))

        actionConfiguracoes = QAction("Configurações", self)
        actionConfiguracoes.triggered.connect(self.config.openConfigurationDialog)

        file_menu.addAction(print_action)
        file_menu.addAction(sort_column)
        file_menu.addAction(delete_row)
        file_menu.addAction(actionConfiguracoes)

    def editarDados(self, item):
        """
        Edit athlete data.

        This method allows the user to edit athlete data by double-clicking on a cell in the table.

        Parameters:
            item (QTableWidgetItem): The selected table item.

        Usage:
        - Double-click on a cell in the table to edit the corresponding athlete's data.
        """

        selected_row = item.row()
        table_widget = item.tableWidget()
        id_value = table_widget.item(selected_row, 0).text()  # Obter valor da primeira coluna (id)

        self.cadastro = cadastroDialog(self.config, self.db, 'update', id_value)
        self.cadastro.exec_()
        
        # Clear tab_widget
        self.tab_widget.clear()

        # reload data with inserted new data
        self.loadData()


    def open_date_picker_dialog(self):
        """
        Open the date picker dialog.

        This method opens a date picker dialog for selecting dates for generating attendance lists.

        Usage:
        - Use the "Gerar Lista de Presença" option from the menu to open the date picker dialog.
        """

        self.dialog = DatePickerDialog(self.print_list)
        self.dialog.show()


    def loadData(self):
        """
        Load athlete data into the table.

        This method retrieves athlete data from the database and populates the table with the data.

        Usage:
        - Called automatically when the application starts to load athlete data.
        """

        table_name = self.config.app_config.database_table_name
        sql_query = f"SELECT * FROM {table_name}"
        cursor = self.db.conn.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(data,columns=column_names)
        
        df['age']=df['dtNascimento'].apply(age)
        categories = {}

        for row in range(len(data)):
            dtNascimento = data[row][5]  # Supondo que a data de nascimento esteja na quinta coluna
            ano_nascimento = int(dtNascimento[-4:])
            categoria = getCat(ano_nascimento, self.config.category_even.isChecked())

            if categoria not in categories:
                categories[categoria] = []

            categories[categoria].append(data[row])

        for category, category_data in categories.items():
            table_widget = AtletasTableWidget(category, category_data, column_names)
            table_widget.table_widget.itemDoubleClicked.connect(self.editarDados)
            self.tab_widget.addTab(table_widget, category)


        cursor.close()

    def save_data(self):
        """
        Check for deleted rows in the table and delete them from the database.
    
        This method checks if any rows have been deleted in the table and deletes
        the corresponding rows from the database.
    
        Usage:
        - Called when changes to athlete data are made and need to be saved.
        """
        table_name = self.config.app_config.database_table_name
        cursor = self.db.conn.cursor()
    
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Collect the IDs of all rows in the table
            existing_ids = set()
            for tab_index in range(self.tab_widget.count()):
                table_widget = self.tab_widget.widget(tab_index)
                for row in range(table_widget.table_widget.rowCount()):
                    item = table_widget.table_widget.item(row, 0)  # Assuming the first column contains unique IDs
                    if item is not None:
                        existing_ids.add(int(item.text()))
    
            # Get the IDs of rows in the database
            cursor.execute(f"SELECT id FROM {table_name}")
            database_ids = set(row[0] for row in cursor.fetchall())
    
            # Calculate the IDs of rows that need to be deleted
            rows_to_delete = database_ids - existing_ids
    
            # Delete rows from the database
            for row_id in rows_to_delete:
                cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
    
            self.db.commit_db()
        except Exception as e:
            self.db.conn.rollback()
            print(f"Error while checking and deleting rows: {str(e)}")
        finally:
            cursor.close()



    def closeEvent(self, event):
        """
        Handle the close event of the main window.

        This method is called when the user attempts to close the application. It provides options to save data
        before closing.

        Parameters:
            event (QCloseEvent): The close event.

        Usage:
        - When the user tries to close the application, a confirmation dialog appears to save data if necessary.
        """

        reply = QMessageBox.question(self, 'Fechar Aplicação', 'Deseja salvar os dados antes de fechar?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            self.save_data()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def delete_selected_row(self):
        """
        Delete selected rows from the table.

        This method allows the user to delete selected rows from the table.

        Usage:
        - Select one or more rows and use the "Deletar Linha" option from the menu to delete them.
        """

        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            table_widget = current_widget.table_widget
            selected_rows = table_widget.selectionModel().selectedRows()
            if len(selected_rows) > 0:
                reply = QMessageBox.question(self, 'Deletar Linha(s)', 'Deseja realmente deletar a(s) linha(s) selecionada(s)?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    for row in selected_rows:
                        table_widget.removeRow(row.row())
                    self.save_data()
                else:
                    QMessageBox.information(self, 'Informação', 'Nenhuma linha foi deletada.')
            else:
                QMessageBox.warning(self, 'Aviso', 'Nenhuma linha selecionada.')
        else:
            QMessageBox.warning(self, 'Aviso', 'Nenhuma tabela selecionada.')
            

    def select_column(self):
        """
        Select a column in the table.

        This method allows the user to select a column in the table.

        Usage:
        - Use the "Selecionar Coluna" option from the menu to select a column.
        """

        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            table_widget = current_widget.table_widget
            selected_columns = table_widget.selectionModel().selectedColumns()
            if len(selected_columns) > 0:
                column_names = [table_widget.horizontalHeaderItem(col).text() for col in selected_columns]
                reply = QMessageBox.information(self, 'Selecionar Coluna', f'Coluna(s) selecionada(s): {", ".join(column_names)}',
                                                QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Aviso', 'Nenhuma coluna selecionada.')
        else:
            QMessageBox.warning(self, 'Aviso', 'Nenhuma tabela selecionada.')


    def sort_column(self):
        """
        Sort a column in the table.

        This method allows the user to sort a column in the table.

        Usage:
        - Click on a column header to sort the data in ascending order.
        - Click again to sort in descending order.
        - Use the "Ordenar Coluna" option from the menu to sort a column.
        """

        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            selected_column = current_widget.table_widget.currentColumn()
            if selected_column >= 0:
                current_widget.table_widget.sortItems(selected_column)
        else:
            QMessageBox.warning(self, 'Aviso', 'Nenhuma tabela selecionada.')

    def search_table(self, text):
        """
        Search for text in the table.

        This method allows the user to search for text in the table and filter the displayed records.

        Parameters:
            text (str): The text to search for.

        Usage:
        - Enter text in the search bar to filter the table records.
        """

        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            table_widget = current_widget.table_widget
            search_text = text.lower()
            for row in range(table_widget.rowCount()):
                row_hidden = True
                for column in range(table_widget.columnCount()):
                    item = table_widget.item(row, column)
                    if item is not None and search_text in item.text().lower():
                        row_hidden = False
                        break
                table_widget.setRowHidden(row, row_hidden)
        else:
            QMessageBox.warning(self, 'Aviso', 'Nenhuma tabela selecionada.')

    def print_dt(self, selected_dates):
        """
        Print selected dates.

        This method generates a PDF file with selected dates.

        Parameters:
            selected_dates (list): The list of selected dates to print.

        Usage:
        - Use the "Imprimir" option to generate a PDF file with the selected dates.
        """

        checkbox_width = 15
        checkbox_x = 50
        checkbox_y = 50
        cell_width = 100

        # Crie um objeto de desenho do ReportLab
        cm=25
        c = canvas.Canvas("output.pdf")

        # Desenhe os checkboxes usando as datas como cabeçalhos
        p=checkbox_x
        for index, date in enumerate(selected_dates):
            #p = checkbox_x + (index + 1) * cell_width
            p = p + 2*checkbox_width
            c.saveState()
            c.rect(p, checkbox_y, checkbox_width, checkbox_width, stroke=1, fill=0)
            c.translate( p + checkbox_width/2, checkbox_y + checkbox_width)
            c.rotate( 45 )
            c.drawString(0, 0, date)
            c.restoreState()

        # Salve o arquivo PDF
        c.save()


    def print_list(self, selected_dates):
        """
        Print an attendance list.

        This method generates an attendance list with checkboxes for selected dates and saves it as a PDF file.

        Parameters:
            selected_dates (list): The list of selected dates for attendance.

        Usage:
        - Use the "Gerar Lista de Presença" option from the menu to generate an attendance list.
        """

        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            table_widget = current_widget.table_widget
            selected_column = table_widget.currentColumn()
            if selected_column >= 0:
                column_name = table_widget.horizontalHeaderItem(selected_column).text()
    
                filename, _ = QFileDialog.getSaveFileName(self, 'Salvar Arquivo PDF', '', 'PDF Files (*.pdf)')
                if filename:
                    c = canvas.Canvas(filename, pagesize=A4)
                    width, height = A4
    
                    #
                    # get month -> convert first selected_date
                    #
                    month = datetime.strptime(selected_dates[0],'%d-%m-%Y').strftime('%B')

                    # Definindo o Cabeçalho

                    c.setFont("Helvetica-Bold", 20)
                    c.drawCentredString(width/2.0, height-2.0*cm, 'Lista de Presença')
                    c.setFont("Helvetica", 16)
                    c.drawCentredString(width/2.0, height-2.5*cm, month )
                    
                    # Obtém o número de linhas na coluna selecionada
                    row_count = table_widget.rowCount()
    
                    # Configurar fontes
                    c.setFont("Helvetica-Bold", 12)
    
                    #
                    # create dataTable
                    #
 
                    dataTable = [ ]
                    
                    # header
                    header = [ 'Nomes ']
                    for date in selected_dates:
                        day = datetime.strptime(date,'%d-%m-%Y').strftime('%d')
                        header.append(day)
                    
                    dataTable.append(header)

                    #
                    # rows
                    #
                    for i in range(row_count):
                        row = [ ]
                        # Obtém o texto da célula atual
                        row.append( table_widget.item(i, selected_column).text() )
                        for date in selected_dates:
                            row.append(' ')
                        
                        dataTable.append(row)


                    t = Table(dataTable)
                    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
                    data_len = len(dataTable)
                    
                    for each in range(data_len):
                        if each % 2 == 0:
                            bg_color = colors.whitesmoke
                        else:
                            bg_color = colors.lightgrey
                    
                        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

                    aW = 540
                    aH = 720
                    styles = getSampleStyleSheet()
                    style = styles["BodyText"]

                    header = Paragraph("<bold><font size=18>TPS Report</font></bold>", style)

                    w, h = header.wrap(aW, aH)
                    #w, h = A4

                    aH = aH - h

                    w, h = t.wrap(aW, aH)
                    t.drawOn(c, 72, aH-h)
                    c.save()
            else:
                QMessageBox.warning(self, 'Imprimir Lista de Presença', 'Por favor, selecione uma coluna.')
    
# Mantenha uma referência global às janelas
splash = None
atletas_app = None

def show_main_window():
    global atletas_app
    splash.close()
    atletas_app = AtletasApp()
    atletas_app.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True) 
    splash = SplashScreen()
    splash.show()
    QTimer.singleShot(2000, show_main_window)
    sys.exit(app.exec_())
#EOC
#-----------------------------------------------------------------------------#

