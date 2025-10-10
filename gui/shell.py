#----------------------------------
#Author: Quinn (Gigawttz)

#What it does: Sets global variables for the native desktop app (window size, resizing, any fun quirks, etc)
#----------------------------------

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
from PySide6.QtCore import Slot, QSize

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
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
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

        self.setMinimumSize(QSize(0, 0))
        self.setMaximumSize(QSize(999999,999999))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
