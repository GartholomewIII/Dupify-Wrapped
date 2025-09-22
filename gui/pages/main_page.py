# gui/pages/main_page.py
from typing import Optional, List, Dict
from PySide6.QtCore import Slot, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QMessageBox, QScrollArea, QWidget, QGridLayout
)


from gui.workers import ArtistCardsWorker, start_worker  # new worker
from gui.widgets.artist_card import ArtistCard           # card widget

def load_stylesheet():
    style_path = Path(__file__).parent / "pages" / "style.qss"
    if style_path.exists():
        with open(style_path, "r") as f:
            return f.read()
    return ""


class MainPage(QWidget):

    def __init__(self):
        super().__init__()
        self.sp = None
        self._thread: Optional[QThread] = None
        self._worker = None

        root = QVBoxLayout(self)

        self.header = QLabel("Spotify Companion — Dashboard")
        


        root.addWidget(self.header)

        self.status = QLabel("Please sign in (previous page).")
        root.addWidget(self.status)

        # Controls
        ctrl = QHBoxLayout()
        self.cmb_view = QComboBox(); self.cmb_view.addItems(["Top Artists (cards)", "Top Genres (list)"])
        self.cmb_range = QComboBox(); self.cmb_range.addItems(["short_term", "medium_term", "long_term"])
        self.spn_limit = QSpinBox(); self.spn_limit.setRange(1, 50); self.spn_limit.setValue(12)
        self.btn_fetch = QPushButton("Fetch"); self.btn_fetch.setEnabled(False); self.btn_fetch.clicked.connect(self.on_fetch_clicked)

        ctrl.addWidget(QLabel("View:"));        ctrl.addWidget(self.cmb_view)
        ctrl.addWidget(QLabel("Time Range:"));  ctrl.addWidget(self.cmb_range)
        ctrl.addWidget(QLabel("Limit:"));       ctrl.addWidget(self.spn_limit)
        ctrl.addWidget(self.btn_fetch)
        root.addLayout(ctrl)

        # Scroll area with grid for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(16)
        self.scroll.setWidget(self.grid_host)
        root.addWidget(self.scroll)

    def set_client(self, sp):
        self.sp = sp
        try:
            me = self.sp.me()
            self.status.setText(f"Signed in as {me.get('display_name')} ({me.get('id')})")
        except Exception:
            self.status.setText("Signed in.")
        self.btn_fetch.setEnabled(True)

    def on_fetch_clicked(self):
        if not self.sp:
            QMessageBox.information(self, "Not signed in", "Please sign in first.")
            return

        # Clear current grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        tr  = self.cmb_range.currentText()
        lim = int(self.spn_limit.value())
        view = self.cmb_view.currentText()

        if view.startswith("Top Artists"):
            self.status.setText("Loading artists…")
            self._worker = ArtistCardsWorker(self.sp, time_range=tr, limit=lim)
            self._thread = start_worker(self, self._worker, self._worker.run)
            self._worker.done.connect(self.on_artist_cards_done)
            self._worker.done.connect(self._thread.quit)
            self._worker.done.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.start()
        else:
            # TODO: wire your genres list (or genre cards) here
            self.status.setText("Top Genres view not wired yet.")

    @Slot(list, object)
    def on_artist_cards_done(self, items: List[Dict[str, Optional[str]]], error):
        if error:
            self.status.setText("Error loading artists")
            QMessageBox.critical(self, "API Error", str(error))
            return
        if not items:
            self.status.setText("No artists found")
            return

        cols = 3
        for i, a in enumerate(items):
            r, c = divmod(i, cols)
            card = ArtistCard(a.get("name", "Unknown"), a.get("image_url"))
            self.grid.addWidget(card, r, c)

        self.status.setText(f"Loaded {len(items)} artists")
