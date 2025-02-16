from PyQt5.QtWidgets import QApplication
import sys
from gui import BarcodeScannerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeScannerApp()
    window.show()
    sys.exit(app.exec_())
