from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

class PopupWindow(QDialog):
    """
    A custom PyQt5 dialog that displays a user interface loaded from "Formulario.ui."

    Parameters:
        parent (QWidget, optional): The parent widget. Defaults to None.

    Usage:
    >>> popup = PopupWindow()
    >>> popup.exec_()
    """

    def __init__(self, parent=None):
        super().__init__()

        # Load the UI file
        uic.loadUi("Formulario.ui", self)
