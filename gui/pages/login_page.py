#------------------------------------
#Author: Quinn (Gigawttz)

#What it Does: Login page for the application, first checkpoint for the spotify API
#Connects the auth methods to the main PySide Desktop App
#------------------------------------
from typing import Optional
from PySide6.QtCore import Signal, Slot, QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from pathlib import Path

from gui.workers import LoginWorker, start_worker


class LoginPage(QWidget):
    """First page: prompts user to sign in. Emits Spotipy client on success."""
    logged_in = Signal(object)  # emits sp

    def __init__(self, parent= None):
        super().__init__(parent)


        # ---------- Background GIF (fills window) ----------
        bg_label = QLabel()
        bg_label.setScaledContents(True)
        bg_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # don't eat clicks
        movie = QMovie(":/pages/assets/background-login.gif")
        bg_label.setMovie(movie)
        movie.start()

        # ---------- Foreground widgets ----------
        self.welcome = QLabel("Dupify")
        self.welcome.setObjectName("welcome")
        self.welcome.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.title = QLabel("Sign in with Spotify")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignHCenter)

        self.btn = QPushButton("SIGN IN")
        self.btn.setObjectName("sign-in-btn")
        self.btn.setMinimumSize(150, 50)
        self.btn.clicked.connect(self.start_login)

        # Optional status line (used by start_login)
        self.status = QLabel("")                       # <---- reintroduced
        self.status.setObjectName("statusLabel")
        self.status.setAlignment(Qt.AlignHCenter)

        # Centered group: title + button + status
        center_group = QVBoxLayout()
        center_group.setSpacing(25)
        center_group.setContentsMargins(0,50,0,0)
        center_group.addWidget(self.title, alignment=Qt.AlignHCenter)
        center_group.addWidget(self.btn, alignment=Qt.AlignHCenter)
        center_group.addWidget(self.status, alignment=Qt.AlignHCenter)

        # Content layout (top welcome + centered group)
        content = QWidget()
        outer = QVBoxLayout(content)
        outer.setContentsMargins(0, 40, 0, 40)
        outer.addWidget(self.welcome, alignment=Qt.AlignHCenter | Qt.AlignTop)
        outer.addStretch(1)
        outer.addLayout(center_group)
        outer.addStretch(2)

        # ---------- Stack background + content ----------
        stack = QStackedLayout(self)
        stack.setStackingMode(QStackedLayout.StackAll)  # draw all layers
        stack.addWidget(bg_label)   # back
        stack.addWidget(content)    # front

        bg_label.lower()
        content.raise_()

        # Ensure foreground can receive focus/clicks
        content.setFocusPolicy(Qt.StrongFocus)


        
    def start_login(self):
        print('loggin in')
        self.status.setText("Opening browser…")
        self.btn.setEnabled(False)

        self._worker = LoginWorker()
        self._thread = start_worker(self, self._worker, self._worker.run)

        self._worker.done.connect(self.on_login_done)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @Slot(object, object)
    def on_login_done(self, sp, error):
        if error:
            self.status.setText("Login failed")
            self.btn.setEnabled(True)
            QMessageBox.critical(self, "Login Error", str(error))
            return

        try:
            me = sp.me()
            self.status.setText(f"Signed in as {me.get('display_name')} ({me.get('id')})")
        except Exception:
            self.status.setText("Signed in.")

        self.logged_in.emit(sp)