import sys
from typing import List, Optional

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QComboBox, QSpinBox, QMessageBox
)

from src.spotify_client import get_spotify_client
from src.user_data import top_artists, genre_breakdown  # <- both return List[str]


# ---------------- Workers ----------------

class LoginWorker(QObject):
    done = Signal(object, object)  # (sp, error)

    @Slot()
    def run(self):
        try:
            sp = get_spotify_client(cache_path=".cache_user")
            self.done.emit(sp, None)
        except Exception as e:
            self.done.emit(None, e)


class TopArtistsWorker(QObject):
    done = Signal(list, object)  # (names: List[str], error)

    def __init__(self, sp, time_range: str, limit: int):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit

    @Slot()
    def run(self):
        try:
            names: List[str] = top_artists(self.sp, limit=self.limit, time_range=self.time_range)
            self.done.emit(names, None)
        except Exception as e:
            self.done.emit([], e)


class TopGenresWorker(QObject):
    done = Signal(list, object)  # (genres: List[str], error)

    def __init__(self, sp, time_range: str, limit: int):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit

    @Slot()
    def run(self):
        try:
            genres: List[str] = genre_breakdown(self.sp, limit=self.limit, time_range=self.time_range)
            self.done.emit(genres, None)
        except Exception as e:
            self.done.emit([], e)


# ---------------- Main Window ----------------

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

        # Controls
        ctrl = QHBoxLayout()

        ctrl.addWidget(QLabel("View:"))
        self.cmb_view = QComboBox()
        self.cmb_view.addItems(["Top Artists", "Top Genres"])
        ctrl.addWidget(self.cmb_view)

        ctrl.addWidget(QLabel("Time Range:"))
        self.cmb_range = QComboBox()
        self.cmb_range.addItems(["short_term", "medium_term", "long_term"])
        ctrl.addWidget(self.cmb_range)

        ctrl.addWidget(QLabel("Limit:"))
        self.spn_limit = QSpinBox()
        self.spn_limit.setRange(1, 50)
        self.spn_limit.setValue(10)
        ctrl.addWidget(self.spn_limit)

        self.btn_fetch = QPushButton("Fetch")
        self.btn_fetch.setEnabled(False)
        self.btn_fetch.clicked.connect(self.on_fetch_clicked)
        ctrl.addWidget(self.btn_fetch)

        root.addLayout(ctrl)

        # Results
        self.list = QListWidget()
        root.addWidget(self.list)

        # Keep references to threads/workers (avoid GC issues)
        self._worker_thread: Optional[QThread] = None
        self._worker_obj: Optional[QObject] = None

    # -------- Login

    def on_login_clicked(self):
        self.status.setText("Signing in…")
        self.btn_login.setEnabled(False)

        t = QThread(self)
        w = LoginWorker()
        w.moveToThread(t)

        t.started.connect(w.run)
        w.done.connect(self.on_login_done)
        w.done.connect(t.quit)
        w.done.connect(w.deleteLater)
        t.finished.connect(t.deleteLater)

        self._worker_thread = t
        self._worker_obj = w

        t.start()

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
            self.status.setText("Login ok, profile fetch failed")
            QMessageBox.warning(self, "Warning", str(e))
            self.btn_login.setEnabled(True)

    # -------- Fetch

    def on_fetch_clicked(self):
        if not self.sp:
            QMessageBox.information(self, "Not signed in", "Please sign in first.")
            return

        self.list.clear()

        view = self.cmb_view.currentText()
        tr = self.cmb_range.currentText()
        lim = int(self.spn_limit.value())

        if view == "Top Artists":
            self.status.setText("Loading top artists…")
            worker = TopArtistsWorker(self.sp, time_range=tr, limit=lim)
        else:
            self.status.setText("Loading top genres…")
            worker = TopGenresWorker(self.sp, time_range=tr, limit=lim)

        t = QThread(self)
        worker.moveToThread(t)

        t.started.connect(worker.run)
        worker.done.connect(self.on_list_done)
        worker.done.connect(t.quit)
        worker.done.connect(worker.deleteLater)
        t.finished.connect(t.deleteLater)

        self._worker_thread = t
        self._worker_obj = worker

        t.start()

    @Slot(list, object)
    def on_list_done(self, items: List[str], error: Optional[Exception]):
        if error:
            self.status.setText("Error loading data")
            QMessageBox.critical(self, "API Error", str(error))
            return

        if not items:
            self.status.setText("No results")
            return

        for i, s in enumerate(items, start=1):
            self.list.addItem(f"{i}. {s}")

        self.status.setText(f"Loaded {len(items)} items")


# ---------------- Entry ----------------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(640, 720)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
