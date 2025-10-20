


    # rec_card.py
from typing import Optional, List

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class RecCard(QWidget):
    """
    Displays a recommended artist with an image and (optional) up to 3 track titles.
    Usage:
        card = RecCard(artist="Yeat", image_url=url, tracks=["Track A", "Track B"])
    """
    def __init__(
        self,
        artist: str,
        genre: str,
        image_url: Optional[str] = None,
        tracks: Optional[List[str]] = None,
        size: int = 160,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._orig_pix: Optional[QPixmap] = None

        self._size = size

        # --- layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        


        # image
        self.img = QLabel()
        self.img.setFixedSize(size, size)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("background-color: rgba(255,34,69,0.42); border-radius: 8px;")
        layout.addWidget(self.img, alignment=Qt.AlignHCenter)

        # artist name (bold)
        self.lbl_artist = QLabel(artist or "Unknown")
        self.lbl_artist.setAlignment(Qt.AlignCenter)
        self.lbl_artist.setWordWrap(True)
        f = QFont()
        f.setPointSize(10)
        f.setBold(True)
        self.lbl_artist.setFont(f)
        layout.addWidget(self.lbl_artist, alignment=Qt.AlignHCenter)

        # optional tracks (small, up to 3)
        self.lbl_tracks = QLabel()
        self.lbl_tracks.setAlignment(Qt.AlignCenter)
        self.lbl_tracks.setWordWrap(True)
        tf = QFont()
        tf.setPointSize(9)
        self.lbl_tracks.setFont(tf)
        layout.addWidget(self.lbl_tracks, alignment=Qt.AlignHCenter)

        if tracks:
            self.set_tracks(tracks)

        if image_url:
            self.set_image_url(image_url)

    # --- public updaters ---
    def set_artist(self, name: str):
        self.lbl_artist.setText(name or "Unknown")

    def set_tracks(self, tracks: List[str]):
        # show at most 3, join with bullets
        tracks = [t for t in (tracks or []) if t][:3]
        self.lbl_tracks.setVisible(bool(tracks))
        if tracks:
            self.lbl_tracks.setText(" • ".join(tracks))
        else:
            self.lbl_tracks.clear()

    def set_image_url(self, url: str):
        if not url:
            return
        reply = self._nam.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(lambda r=reply: self._on_loaded(r))

    # --- internals ---
    def _on_loaded(self, reply):
        data = reply.readAll()
        reply.deleteLater()
        img = QImage.fromData(bytes(data))
        if img.isNull():
            return
        self._orig_pix = QPixmap.fromImage(img)
        self._rescale()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._rescale()

    def _rescale(self):
        if not self._orig_pix:
            return
        w = max(1, self.img.width())
        h = max(1, self.img.height())
        scaled = self._orig_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.img.setPixmap(scaled)
