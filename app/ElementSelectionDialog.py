from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class ElementSelectionDialog(QDialog):
    """
    A dialog for element selection.

    Allows the user to select elements from a list and returns the selected elements.

    Args:
        elements (list): A list of elements for selection.

    Usage:
        >>> dialog = ElementSelectionDialog(["Element 1", "Element 2", "Element 3"])
        >>> result = dialog.exec_()
        >>> if result == QDialog.Accepted:
        >>>     selected_elements = dialog.selected_elements
        >>>     print("Selected elements:", selected_elements)
    """

    def __init__(self, elements):
        """
        Initialize the ElementSelectionDialog.

        Args:
            elements (list): A list of elements for selection.
        """
        super().__init__()

        self.elements = elements

        self.left_list_widget = QListWidget()
        self.right_list_widget = QListWidget()

        self.select_button = QPushButton("Selecionar ->")
        self.deselect_button = QPushButton("<- Deselecionar")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.clear_button = QPushButton("Limpar Seleção")
        self.get_selected_items_button = QPushButton("Obter Itens Selecionados")
        self.select_all_button = QPushButton("Selecionar Todos")

        self.select_button.clicked.connect(self.move_selected_items_to_right)
        self.deselect_button.clicked.connect(self.move_selected_items_to_left)
        self.ok_button.clicked.connect(self.save_selected_elements)
        self.cancel_button.clicked.connect(self.reject)
        self.clear_button.clicked.connect(self.clear_selection)
        self.get_selected_items_button.clicked.connect(self.show_selected_items)
        self.select_all_button.clicked.connect(self.select_all_items)

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface of the element selection dialog.
        """
        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.left_list_widget)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_list_widget)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(self.deselect_button)
        buttons_layout.addWidget(self.clear_button)
        #buttons_layout.addWidget(self.get_selected_items_button)
        buttons_layout.addWidget(self.select_all_button)

        layout.addLayout(left_layout)
        layout.addLayout(buttons_layout)
        layout.addLayout(right_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.setWindowTitle("Element Selection")

        # Fill the left list with the provided elements
        self.left_list_widget.addItems(self.elements)

    def move_selected_items_to_right(self):
        """
        Move selected items from the left list to the right list.
        """
        selected_items = self.left_list_widget.selectedItems()
        for item in selected_items:
            self.left_list_widget.takeItem(self.left_list_widget.row(item))
            self.right_list_widget.addItem(item)

    def move_selected_items_to_left(self):
        """
        Move selected items from the right list to the left list.
        """
        selected_items = self.right_list_widget.selectedItems()
        for item in selected_items:
            self.right_list_widget.takeItem(self.right_list_widget.row(item))
            self.left_list_widget.addItem(item)

    def save_selected_elements(self):
        """
        Get the selected elements from the dialog.

        Returns:
            list: A list of selected elements.
        """
        selected_elements = [self.right_list_widget.item(i).text() for i in range(self.right_list_widget.count())]
        self.selected_elements = selected_elements
        self.accept()

    def clear_selection(self):
        """
        Clear the selection in the right list widget.
        """
        self.right_list_widget.clear()
        self.left_list_widget.addItems(self.elements)

    def show_selected_items(self):
        """
        Show a message box with the selected items and associated data.
        """
        selected_items = self.get_selected_items_with_data()
        message = "Selected Items:\n\n"
        for item_text, item_data in selected_items:
            message += f"Item: {item_text}, Data: {item_data}\n"
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Selected Items")
        msg_box.setText(message)
        msg_box.exec_()

    def get_selected_items_with_data(self):
        """
        Get selected items from the right list widget along with associated data.

        Returns:
            list: A list of tuples (element_text, element_data) for selected items.
        """
        selected_items = []
        for i in range(self.right_list_widget.count()):
            item = self.right_list_widget.item(i)
            selected_items.append((item.text(), item.data(Qt.UserRole)))
        return selected_items

    def select_all_items(self):
        """
        Select all items in the left list (items available) and move them to the right list (items selected).
        """
        count = self.left_list_widget.count()
        for i in range(count):
            item = self.left_list_widget.item(0)  # Pegue sempre o primeiro item para evitar problemas de índice
            self.left_list_widget.takeItem(0)
            self.right_list_widget.addItem(item)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])

    dialog = ElementSelectionDialog(["Element 1", "Element 2", "Element 3"])
    result = dialog.exec_()

    if result == QDialog.Accepted:
        selected_elements = dialog.selected_elements
        print("Selected elements:", selected_elements)

    app.exec_()

