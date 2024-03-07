from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,QHBoxLayout, QAbstractItemView, QPushButton, QMenu, QAction, QDialog, QCheckBox
from PyQt5.QtCore import Qt

import re
from .whatsapp import sendMessage


from .ElementSelectionDialog import ElementSelectionDialog
from .PreSumulaGenerator import FutsalPreSumulaGenerator
from .autorizacao_menor_liga import create_authorization_form

class AtletasTableWidget(QWidget):
    def __init__(self, category, data, column_names, visible_columns=None):
        """
        Cria uma tabela de dados a partir dos dados fornecidos.

        Args:
            data (list): Uma lista de listas contendo os dados a serem exibidos na tabela.
            column_names (list): Uma lista de nomes de colunas correspondentes aos dados.
            visible_columns (list, opcional): Uma lista de nomes de colunas a serem exibidos. 
                Se não especificado, todas as colunas serão visíveis.

        Uso:
        >>> app = QApplication(sys.argv)
        >>> category = 'sub-13'
        >>> data = [[1, 'John', 'Doe', 'New York'], [2, 'Jane', 'Smith', 'Los Angeles']]
        >>> columns = ['ID', 'First Name', 'Last Name', 'City']
        >>> visible_columns = ['ID', 'First Name', 'Last Name']  # Colunas visíveis
        >>> table_widget = AtletasTableWidget(category,data, columns, visible_columns)
        >>> table_widget.show()
        >>> sys.exit(app.exec_())
        """
        super().__init__()

        self.category_name = category
        self.column_names = column_names
        self.visible_columns = visible_columns if visible_columns else column_names
        self.original_data = data

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.table_widget.setColumnCount(len(self.visible_columns))
        self.table_widget.setHorizontalHeaderLabels(self.visible_columns)

        self.layout = QVBoxLayout()

        self.populate_table(data)

        # Botões para adicionar, excluir e classificar
        button_layout = QHBoxLayout()
        self.addButton = QPushButton("Adicionar Linha")
        self.addButton.clicked.connect(self.add_row)
        self.deleteButton = QPushButton("Excluir Linha")
        self.deleteButton.clicked.connect(self.delete_selected_row)
        # Botão para classificar por coluna
        self.sortButton = QPushButton("Classificar por...")
        self.sortButton.clicked.connect(self.show_column_menu)
        
        self.presumulaButton = QPushButton("Criar Pré-Sumula")
        self.presumulaButton.clicked.connect(self.create_presumula)

        self.authFormButton = QPushButton("Gerar Fomulario")
        self.authFormButton.clicked.connect(self.create_form)

        button_layout.addWidget(self.addButton)
        button_layout.addWidget(self.deleteButton)
        button_layout.addWidget(self.sortButton)
        button_layout.addWidget(self.presumulaButton)
        button_layout.addWidget(self.authFormButton)

        # Adicionar botão para seleção de colunas
        self.select_columns_button = QPushButton("Selecionar Colunas", self)
        self.select_columns_button.clicked.connect(self.open_column_selection_dialog)
        self.layout.addWidget(self.select_columns_button)

        self.layout.addWidget(self.table_widget)
        self.layout.addLayout(button_layout)  # Adicione o layout dos botões à janela principal
        self.setLayout(self.layout)

        # Conecte o sinal de clique de cabeçalho de coluna a um slot para exibir o menu pop-up
        self.table_widget.horizontalHeader().sectionClicked.connect(self.show_column_menu)

    def open_column_selection_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Colunas")
        layout = QVBoxLayout(dialog)

        # Criar caixas de seleção para cada coluna
        checkboxes = {}
        for name in self.column_names:
            checkbox = QCheckBox(name, dialog)
            layout.addWidget(checkbox)
            checkboxes[name] = checkbox

        # Adicionar botão de confirmar
        confirm_button = QPushButton("Confirmar", dialog)
        confirm_button.clicked.connect(lambda: self.update_visible_columns(checkboxes, dialog))
        layout.addWidget(confirm_button)

        dialog.exec_()

    def update_visible_columns(self, checkboxes, dialog):
        selected_columns = [name for name, checkbox in checkboxes.items() if checkbox.isChecked()]
        for col_index in range(self.table_widget.columnCount()):
            col_name = self.table_widget.horizontalHeaderItem(col_index).text()
            self.table_widget.setColumnHidden(col_index, col_name not in selected_columns)
        dialog.accept()

    def show_column_menu(self, column):
        """
        Exibe um menu pop-up quando uma coluna é clicada com opções de classificação,
        exclusão e cópia do valor da célula.

        Args:
            column (int): O índice da coluna clicada.

        Uso:
        >>> # O menu pop-up será exibido ao clicar no cabeçalho de uma coluna.
        """
        # Crie um menu pop-up
        menu = QMenu(self)

        # Opções de classificação
        sort_menu = menu.addMenu("Classificar por...")
        for column_name in self.visible_columns:
            sort_action = QAction(column_name, self)
            sort_action.triggered.connect(lambda _, col=column_name: self.sort_table_by_column(col))
            sort_menu.addAction(sort_action)

#        # Opção de exclusão de linha
#        delete_action = QAction("Excluir Linha", self)
#        delete_action.triggered.connect(self.delete_selected_row)
#        menu.addAction(delete_action)
#
#        # Opção de cópia do valor da célula
#        selected_items = self.table_widget.selectedItems()
#        if len(selected_items) == 1:
#            copy_value_action = QAction(f"Copiar {selected_items[0].text()}", self)
#            copy_value_action.triggered.connect(lambda _, item=selected_items[0]: self.copy_cell_value(item))
#            menu.addAction(copy_value_action)

        # Exiba o menu pop-up na posição do cursor
        menu.exec_(self.cursor().pos())

    def populate_table(self, data):
        """
        Preenche a tabela com os dados fornecidos.

        Args:
            data (list): Uma lista de listas contendo os dados a serem exibidos na tabela.
        """
        self.table_widget.setRowCount(len(data))
        for row in range(len(data)):
            for column in range(len(self.visible_columns)):
                column_name = self.visible_columns[column]
                column_index = self.column_names.index(column_name)
                item = QTableWidgetItem(str(data[row][column_index]))
                self.table_widget.setItem(row, column, item)

    def get_selected_data(self):
        """
        Retorna os dados da linha selecionada na tabela.

        Returns:
            list: Uma lista com os dados da linha selecionada.

        Uso:
        >>> selected_data = table_widget.get_selected_data()
        """
        selected_rows = []
        for selected_item in self.table_widget.selectedItems():
            row = selected_item.row()
            selected_row = [self.table_widget.item(row, col).text() for col in range(self.table_widget.columnCount())]
            selected_rows.append(selected_row)
        return selected_rows

    def add_row(self):
        """
        Adiciona uma nova linha vazia à tabela.

        Uso:
        >>> table_widget.add_row()
        """
        self.table_widget.insertRow(self.table_widget.rowCount())
        for column in range(self.table_widget.columnCount()):
            item = QTableWidgetItem('')
            self.table_widget.setItem(self.table_widget.rowCount() - 1, column, item)

    def delete_selected_row(self):
        """
        Exclui a linha selecionada na tabela.

        Uso:
        >>> table_widget.delete_selected_row()
        """
        selected_rows = self.table_widget.selectionModel().selectedRows()
        for row in selected_rows:
            self.table_widget.removeRow(row.row())

    def sort_table(self):
        """
        Classifica a tabela com base na coluna de Nome, em ordem alfabética crescente.

        Uso:
        >>> table_widget.sort_table()
        """
        self.table_widget.sortByColumn(1, Qt.AscendingOrder)
        
    def sort_table_by_column(self, column_name):
        """
        Classifica a tabela com base na coluna fornecida.

        Args:
            column_name (str): O nome da coluna pela qual a tabela será classificada.

        Uso:
        >>> table_widget.sort_table_by_column("Nome")
        """
        # Encontre o índice da coluna pelo nome
        if column_name in self.visible_columns:
            column_index = self.visible_columns.index(column_name)
    
            # Classifique a tabela com base na coluna
            self.table_widget.sortItems(column_index, Qt.AscendingOrder)

    def filter_table(self, filter_text):
        """
        Filtra os dados na tabela com base em um texto de filtro fornecido.

        Args:
            filter_text (str): O texto de filtro a ser aplicado.

        Uso:
        >>> table_widget.filter_table("John")
        """
        for row in range(self.table_widget.rowCount()):
            should_show = False
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                if item and filter_text.lower() in item.text().lower():
                    should_show = True
                    break
            self.table_widget.setRowHidden(row, not should_show)

    def resize_columns_to_fit(self):
        """
        Redimensiona automaticamente as colunas da tabela para ajustar ao conteúdo.

        Uso:
        >>> table_widget.resize_columns_to_fit()
        """
        self.table_widget.resizeColumnsToContents()

    def get_row_count(self):
        """
        Retorna o número total de linhas na tabela.

        Returns:
            int: O número total de linhas na tabela.

        Uso:
        >>> row_count = table_widget.get_row_count()
        """
        return self.table_widget.rowCount()

    def create_presumula(self):
        """
        Create a Pre-Summary based on selected elements.

        Opens a dialog to select elements from the 'nome' column and create a Pre-Summary.

        Test Case:
            >>> app = QApplication([])
            >>> data = [['John'], ['Jane'], ['Alice'], ['Bob']]
            >>> columns = ['nome']
            >>> table_widget = AtletasTableWidget(data, columns)
            >>> table_widget.show()
            >>> table_widget.create_presumula()
            >>> # User selects 'John' and 'Alice' in the dialog, 'Selected elements: ['John', 'Alice']' will be printed.
            >>> app.exec_()
        """
        # Get the data from the 'nome' column
        column_index = self.column_names.index('nome')
        data = [self.table_widget.item(row, column_index).text() for row in range(self.table_widget.rowCount())]

        # Create the element selection dialog and get the selected elements
        dialog = ElementSelectionDialog(data)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            selected_elements = dialog.selected_elements
            print("Selected elements:", selected_elements)

            # Generate the Pre-Summary with category name
            presumula_generator = FutsalPreSumulaGenerator()
            athletes_data = [['', name] for name in selected_elements]  # Number column is left blank
            presumula_generator.generate_pre_sumula(athletes_data, self.category_name)
            #presumula_generator.visualize_pdf('Final_Futsal_Scoresheet.pdf')
        else:
            print("Pre-Summary creation canceled by the user.")

    def create_form(self):
        """
        Create an authorization form for selected athletes.

        Opens a dialog to select athletes from the 'nome' column, and creates an authorization form for each.
        """
        # Get the data from the 'nome' column
        column_index_nome = self.column_names.index('nome')
        data = [self.table_widget.item(row, column_index_nome).text() for row in range(self.table_widget.rowCount())]

        # Create the element selection dialog and get the selected elements
        dialog = ElementSelectionDialog(data)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            selected_elements = dialog.selected_elements
            print("Selected elements:", selected_elements)

            for element in selected_elements:
                # Gather all information for the selected athlete
                athlete_data = {}
                for column_name in self.column_names:
                    column_index = self.column_names.index(column_name)
                    athlete_data[column_name] = self.table_widget.item(data.index(element), column_index).text()

                telefone = athlete_data['foneContato']
                
                # Remover caracteres não numéricos
                numero_limpo = re.sub(r'\D', '', telefone)
                if numero_limpo and len(numero_limpo) > 2:
                    # Adicionar código de país
                    tel = "+55" + numero_limpo
                    nome = athlete_data['nome'].split()[0]
                    print(f'{nome} {tel}')
                    # Create the filename for the PDF
                    filename = f'authorization_form_{athlete_data["nome"].replace(" ", "_")}.pdf'
    
                    # Generate the authorization form PDF for this athlete
                    create_authorization_form(filename, athlete_data)

                    sendMessage(tel,nome)
                
        else:
            print("Authorization form creation canceled by the user.")
