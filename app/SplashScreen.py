import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

from .paths import path

class SplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(SplashScreen, self).__init__()
        uiFile = os.path.join(path.ui, "banner.ui")
        uic.loadUi(uiFile, self)
        # Timer para fechar a SplashScreen depois de 10 segundos
        QTimer.singleShot(5000, self.close)
