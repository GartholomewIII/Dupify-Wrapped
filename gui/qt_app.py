import sys
from typing import List, Dict, Any
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QComboBox, QSpinBox, QTabWidget, QMessageBox
)

from src.spotify_client import get_spotify_client
from src.user_data import (
    top_artists, genre_breakdown, top_tracks, top_tracks
)

class LoginWorker(QObject):
    done = Signal(object, object)  # (sp_or_none, error_or_none)

    @Slot()
    def run(self):
        try:
            sp = get_spotify_client(cache_path=".cache_user")
            self.done.emit(sp, None)
        except Exception as e:
            self.done.emit(None, e)


class TopArtistsWorker(QObject):
    done = Signal(list, object)  # (items, error)

    def __init__(self, sp, time_range: str, limit: int, offset: int = 0):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit
        self.offset = offset

    @Slot()
    def run(self):
        try:
            resp: Dict[str, Any] = top_artists(
                self.sp, limit=self.limit, time_range=self.time_range, offset=self.offset
            )
            items: List[Dict[str, Any]] = resp.get("items", [])
            self.done.emit(items, None)
        except Exception as e:
            self.done.emit([], e)


# ---------- Main Window ----------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Companion — Native")
        self.sp = None

        root = QVBoxLayout(self)

        # Status + Login
        self.status = QLabel("Not signed in")
        root.addWidget(self.status)

        row = QHBoxLayout()
        self.btn_login = QPushButton("Sign in with Spotify")
        self.btn_login.clicked.connect(self.on_login_clicked)
        row.addWidget(self.btn_login)
        root.addLayout(row)

        # Controls for Top Artists
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Time Range:"))
        self.cmb_range = QComboBox()
        self.cmb_range.addItems(["short_term", "medium_term", "long_term"])
        ctrl.addWidget(self.cmb_range)

        ctrl.addWidget(QLabel("Limit:"))
        self.spn_limit = QSpinBox()
        self.spn_limit.setRange(1, 50)
        self.spn_limit.setValue(10)
        ctrl.addWidget(self.spn_limit)

        self.btn_fetch = QPushButton("Fetch Top Artists")
        self.btn_fetch.clicked.connect(self.on_fetch_artists)
        self.btn_fetch.setEnabled(False)
        ctrl.addWidget(self.btn_fetch)

        root.addLayout(ctrl)

        # Results list
        self.list = QListWidget()
        root.addWidget(self.list)

    # ---------- Slots ----------

    def on_login_clicked(self):
        self.status.setText("Signing in...")
        self.btn_login.setEnabled(False)

        self.login_thread = QThread(self)
        self.login_worker = LoginWorker()
        self.login_worker.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.login_worker.run)
        self.login_worker.done.connect(self.on_login_done)
        self.login_worker.done.connect(self.login_thread.quit)
        self.login_worker.done.connect(self.login_worker.deleteLater)
        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.start()

    @Slot(object, object)
    def on_login_done(self, sp, error):
        if error:
            self.status.setText("Login failed")
            self.btn_login.setEnabled(True)
            QMessageBox.critical(self, "Login Error", str(error))
            return

        self.sp = sp
        try:
            me = self.sp.me()
            self.status.setText(f"Signed in as {me.get('display_name')} ({me.get('id')})")
            self.btn_fetch.setEnabled(True)
        except Exception as e:
            self.status.setText("Login succeeded, profile fetch failed")
            QMessageBox.warning(self, "Warning", f"Could not fetch profile: {e}")
            self.btn_login.setEnabled(True)

    def on_fetch_artists(self):
        if not self.sp:
            QMessageBox.information(self, "Not signed in", "Please sign in first.")
            return

        self.list.clear()
        self.status.setText("Loading top artists...")

        tr = self.cmb_range.currentText()
        lim = int(self.spn_limit.value())

        self.artists_thread = QThread(self)
        self.artists_worker = TopArtistsWorker(self.sp, time_range=tr, limit=lim)
        self.artists_worker.moveToThread(self.artists_thread)
        self.artists_thread.started.connect(self.artists_worker.run)
        self.artists_worker.done.connect(self.on_artists_done)
        self.artists_worker.done.connect(self.artists_thread.quit)
        self.artists_worker.done.connect(self.artists_worker.deleteLater)
        self.artists_thread.finished.connect(self.artists_thread.deleteLater)
        self.artists_thread.start()

    @Slot(list, object)
    def on_artists_done(self, items, error):
        if error:
            self.status.setText("Error loading artists")
            QMessageBox.critical(self, "API Error", str(error))
            return

        if not items:
            self.status.setText("No artists returned")
            return

        for i, a in enumerate(items, start=1):
            name = a.get("name", "Unknown")
            pop = a.get("popularity", "—")
            genres = ", ".join(a.get("genres", []))
            self.list.addItem(f"{i}. {name}  (pop {pop})  [{genres}]")

        self.status.setText(f"Loaded {len(items)} artists")


# ---------- Entry Point ----------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(640, 720)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()