#---------------------------------------
#Author: Quinn (Gigawttz)

#What this does: Constructs a qt obj like that in artist_card.py which displays top tracks
#in a 3x? grid to be displayed on the main page
#---------------------------------------

from typing import Optional
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

class TrackCard(QWidget):
    def __init__(self, artist: str, track: str, image_url: Optional[str], size: int = 160, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._orig_pix: Optional[QPixmap] = None
        self._cover_size = size

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 10)
        layout.setSpacing(6)

        self.img = QLabel()
        self.img.setFixedSize(size, size)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.img.setStyleSheet("background-color: rgba(255,34,69,0.42); border-radius: 8px;")
        layout.addWidget(self.img, alignment=Qt.AlignHCenter)

        self.caption = QLabel(f"{artist or 'Unknown'} - {track or 'Unknown'}")
        self.caption.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.caption.setWordWrap(True)
        self.caption.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.caption.setFixedWidth(size)
        f = QFont(); f.setPointSize(10); f.setBold(True)
        self.caption.setFont(f)
        layout.addWidget(self.caption, alignment=Qt.AlignHCenter)

        if image_url:
            reply = self._nam.get(QNetworkRequest(QUrl(image_url)))
            reply.finished.connect(lambda r=reply: self._on_loaded(r))

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
        scaled = self._orig_pix.scaled(
            self._cover_size, self._cover_size,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.img.setPixmap(scaled)
