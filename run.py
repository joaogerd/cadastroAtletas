import sys
from PyQt5.QtWidgets import QApplication
from app.AtletasApp import AtletasApp  # Importe AtletasApp do diretório app

if __name__ == "__main__":
    app = QApplication(sys.argv)
    atletas_app = AtletasApp()
    atletas_app.show()
    sys.exit(app.exec_())
