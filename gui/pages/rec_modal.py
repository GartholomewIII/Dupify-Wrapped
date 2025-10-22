from typing import Optional, List
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QListWidget,
    QDialogButtonBox, QSizePolicy, QWidget
)


class RecModal(QDialog):

    def __init__(self, artist, tracks, image_url, parent= None):

        super().__init__(parent)
        self.setWindowTitle(f"{artist} Recommendations")

        self._nam = QNetworkAccessManager(self)
        self._orig_pix = None

        self._tracks = (tracks or [])[:3]
        self._image_url = image_url

        #Layout
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QVBoxLayout()
        self.img= QLabel()
        self.img.setFixedSize(240,240)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        left.addWidget(self.img, alignment= Qt.AlignTop | Qt.AlignLeft)
        root.addLayout(left)


        right = QVBoxLayout()
        right.setSpacing(8)

        title= QLabel(artist or 'Unknown')
        f = QFont(); f.setPointSize(12); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        right.addWidget(title)

        self.list = QListWidget()
        self.list.setUniformItemSizes(True)
        self.list.setAlternatingRowColors(True)

        for t in (tracks or [])[:3]:
            if t:
                self.list.addItem(t)

        right.addWidget(self.list)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        right.addWidget(btns, alignment= Qt.AlignRight)

        root.addLayout(right)


        if image_url:
            reply= self._nam.get(QNetworkRequest(QUrl(image_url)))
            reply.finished.connect(lambda r= reply: self._on_loaded(r))

        self.resize(self.sizeHint().width() + 80, max(320, self.sizeHint().height()))
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self._artist, self._tracks, self._image_url, self._genre)
        super().mousePressEvent(e)

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
        w = self.img.width()
        h = self.img.height()
        scaled = self._orig_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.img.setPixmap(scaled)