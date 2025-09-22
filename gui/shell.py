from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Slot

from gui.pages.login_page import LoginPage
from gui.pages.main_page import MainPage


class Shell(QWidget):
    """Container that swaps between LoginPage and MainPage."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Companion")

        self.setFixedSize(500,500)
        self._center_on_screen()

        self.stack = QStackedWidget(self)
        self.login_page = LoginPage()
        self.main_page = MainPage()

        self.stack.addWidget(self.login_page)  # 0
        self.stack.addWidget(self.main_page)   # 1

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

        self.login_page.logged_in.connect(self.on_logged_in)

    @Slot(object)


    def _center_on_screen(self):
        """Center this window on the current screen (multi-monitor safe)."""
        screen = self.screen() or QApplication.primaryScreen()
        center = screen.availableGeometry().center()
        frame = self.frameGeometry()             # type: QRect
        frame.moveCenter(center)
        self.move(frame.topLeft())


    def on_logged_in(self, sp):
        self.main_page.set_client(sp)
        self.stack.setCurrentIndex(1)

        '''
        self.setMinimumSize(800, 600)
        self.setMaximumSize(16777215, 16777215)  # removes previous fixed bound
        self.resize(1000, 800)
        '''
        self.showFullScreen()
