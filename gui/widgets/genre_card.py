#-----------------------------------------
#Author Name: Quinn (Gigawttz)

#What this does: Creates a genre card obj that in best cases displays a cooresponding banner
#in worst cases it displays a prominent artist in that genre
#-----------------------------------------


from typing import Optional
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout, QSizePolicy

class GenreBannerCard(QWidget):
    """
    Full-width banner (e.g., 1×3 stack). Scales image on resize, keeps text readable.
    """
    def __init__(self, genre: str, image_url: Optional[str], height: int = 140, parent=None):

        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._orig_pix: Optional[QPixmap] = None

        # ensure it expands horizontally
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(height)
        self.setMaximumHeight(max(height, 220))  # allow a little room if parent stretches

        container = QWidget(self)
        container_layout = QStackedLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setStackingMode(QStackedLayout.StackAll)

        self.img = QLabel()
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("background-color: rgba(255, 34, 69, 0.25);")
        container_layout.addWidget(self.img)

        self.title = QLabel(genre or "Unknown")
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title.setWordWrap(True)
        self.title.setStyleSheet(
            "color: white; padding: 12px 16px; "
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(0,0,0,0.45), stop:1 rgba(0,0,0,0.65)); "
        )
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        self.title.setFont(f)
        container_layout.addWidget(self.title)
        self.title.raise_()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(8)
        outer.addWidget(container)

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
        # Fill width, keep aspect ratio, crop vertically if needed (like CSS cover)
        w = max(1, self.img.width())
        h = max(1, self.img.height())
        scaled = self._orig_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.img.setPixmap(scaled)
    