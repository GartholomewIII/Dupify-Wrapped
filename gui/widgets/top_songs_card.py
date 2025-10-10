#---------------------------------------
#Author: Quinn (Gigawttz)

#What this does: Constructs a qt obj like that in artist_card.py which displays top tracks
#in a 3x? grid to be displayed on the main page
#---------------------------------------

from typing import Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class TrackCard(QWidget):
    def __init__(self, artist: str, track: str, image_url: Optional[str], size: int = 160, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.img = QLabel()
        self.img.setFixedSize(size, size)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("background-color: rgba(255,34,69,0.42); border-radius: 8px;")
        layout.addWidget(self.img, alignment=Qt.AlignHCenter)

        self.caption = QLabel(f"{artist or 'Unknown'} - {track or 'Unknown'}")
        self.caption.setAlignment(Qt.AlignCenter)
        self.caption.setWordWrap(True)
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
        pix = QPixmap.fromImage(img).scaled(
            self.img.width(), self.img.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.img.setPixmap(pix)
