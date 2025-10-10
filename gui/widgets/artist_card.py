#-------------------------------------------
#Author: Quinn (Gigawttz)

#What this does: Creates a artist card Qt Obj that displays a top artist
#-------------------------------------------


from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ArtistCard(QWidget):
    def __init__(self, name: str, image_url: str | None, size: int = 160, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._orig_pix: Optional[QPixmap] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.img = QLabel()
        self.img.setFixedSize(size, size)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("background-color: rgba(255, 34, 69, 0.42); border-radius: 8px;")
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
