# gui/widgets/artist_card.py
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ArtistCard(QWidget):
    def __init__(self, name: str, image_url: str | None, size: int = 160, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.img = QLabel()
        self.img.setFixedSize(size, size)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("background: #222; border-radius: 8px;")
        layout.addWidget(self.img, alignment=Qt.AlignHCenter)

        self.name = QLabel(name or "Unknown")
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setWordWrap(True)
        layout.addWidget(self.name, alignment=Qt.AlignHCenter)

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
