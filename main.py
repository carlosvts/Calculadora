import sys

from buttons import ButtonsGrid
from constants import WINDOW_ICON_PATH
from display import Display
from info import Info
from main_window import MainWindow
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from styles import setupTheme

if __name__ == "__main__":
    # Cria aplicação
    app = QApplication(sys.argv)
    setupTheme()
    window = MainWindow()

    # Setando o ícone
    icon = QIcon(str(WINDOW_ICON_PATH))
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)

    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            u'CompanyName.ProductName.SubProduct.VersionInformation')

    # Info
    info = Info("Sua conta: ")
    window.addWidgetToVLayout(info)

    # Display
    display = Display()
    window.addWidgetToVLayout(display)

    # Grid
    buttons_grid = ButtonsGrid(display=display, info=info, window=window)
    window.v_layout.addLayout(buttons_grid)

    # executa tudo
    window.adjustFixedSize()
    window.show()
    app.exec()
