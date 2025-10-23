#------------------------------------
#Author: Quinn (Gigawttz)

#What it Does: Main page that is launched after sign in
#Displays user spotify data
#------------------------------------


from typing import Optional, List, Dict
from PySide6.QtCore import Slot, QThread, Qt, QUrl, QRectF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedLayout,
    QComboBox, QSpinBox, QMessageBox, QScrollArea, QWidget, QGridLayout, QGraphicsView, QGraphicsScene, QFrame
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtGui import QFont


from pathlib import Path

from gui.workers import ArtistCardsWorker, GenreCardsWorker, TopTracksWorker,RecommendArtistTrackWorker, start_worker  # new worker

from gui.widgets.artist_card import ArtistCard
from gui.widgets.genre_card import GenreBannerCard   
from gui.widgets.top_songs_card import TrackCard
from gui.widgets.reccomend_card import RecCard
from .rec_modal import RecModal
        

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
        

        #----------BACKGROUND VIDEO-----------
        self._scene = QGraphicsScene(self)
        self._view  = QGraphicsView(self._scene, self)
        self._view.setFrameShape(QFrame.NoFrame)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._video_item = QGraphicsVideoItem()
        self._video_item.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        self._scene.addItem(self._video_item)

        self._player = QMediaPlayer()
        self._audio  = QAudioOutput()
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video_item)

        mp4 = Path(__file__).parent / "assets" / "background-vid.mp4"
        self._player.setSource(QUrl.fromLocalFile(str(mp4)))
        self._audio.setMuted(True)
        self._player.play()
        self._player.mediaStatusChanged.connect(
            lambda s: self._player.play() if s == QMediaPlayer.EndOfMedia else None
        )

        #--------FOREGROUND ITEMS----------------
        content= QWidget()
        root = QVBoxLayout(content)
    

        

        #--------LABELS--------------------------
        self.header = QLabel("Dupify")
        root.addWidget(self.header)
        self.header.setObjectName("main-pg-header")

        self.status = QLabel("Please sign in (previous page).")
        root.addWidget(self.status)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setObjectName('control-labels')

        self.cmb_view = QComboBox(); self.cmb_view.addItems(["Top Artists", "Top Genres", "Top Tracks", "Recommend More"])
        self.cmb_view.setObjectName('mode')

        #changes cmb val if the selector is reccomended
    

        
        self.time_range_dict = {'3 Months': 'short_term', '6 Months': 'medium_term', 'One Year': 'long_term'}
        self.cmb_range = QComboBox(); self.cmb_range.addItems(["3 Months", "6 Months", "One Year"])
        self.cmb_range.setObjectName('time-length')



        self.spn_limit = QSpinBox(); self.spn_limit.setRange(1, 20); self.spn_limit.setValue(12)
        self.spn_limit.setObjectName('num-lim')

        self.btn_fetch = QPushButton("Fetch"); self.btn_fetch.setEnabled(False); self.btn_fetch.clicked.connect(self.on_fetch_clicked)
        self.btn_fetch.setObjectName('fetch-btn')

        self.view_label = QLabel('View:')
        self.view_label.setObjectName('view-label')
        ctrl.addWidget(self.view_label);        ctrl.addWidget(self.cmb_view)
        
        self.time_label = QLabel('Time Range:')
        self.time_label.setObjectName('time-label')
        ctrl.addWidget(self.time_label);  ctrl.addWidget(self.cmb_range)

        self.limit_label = QLabel('Limit:')
        self.limit_label.setObjectName('limit-label')
        ctrl.addWidget(self.limit_label);       ctrl.addWidget(self.spn_limit)
        ctrl.addWidget(self.btn_fetch)
        root.addLayout(ctrl)

        self._rec_hideables = [
            self.time_label, self.cmb_range,
            self.limit_label, self.spn_limit
            ]



        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
            

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
            

        self.grid.setHorizontalSpacing(16)
        self.scroll.setWidget(self.grid_host)
        root.addWidget(self.scroll)
        
        stack = QStackedLayout(self)
        stack.setStackingMode(QStackedLayout.StackAll)
        
        stack.addWidget(self._view)
        stack.addWidget(content)

        stack.setCurrentWidget(content)

        
        self.cmb_view.currentTextChanged.connect(self._on_view_changed)
        self._on_view_changed(self.cmb_view.currentText())
    def set_client(self, sp):
        self.sp = sp
        try:
            me = self.sp.me()
            self.status.setText(f"Signed in as {me.get('display_name')} ({me.get('id')})")
        except Exception:
            self.status.setText("Signed in.")
        self.btn_fetch.setEnabled(True)

    def _on_view_changed(self, text: str):
        show_time  = (text != "Recommend More")
        self.time_label.setVisible(show_time)
        self.cmb_range.setVisible(show_time)

        # limit shown only for "Top Artists" and "Top Tracks"
        show_limit = (text in ("Top Artists", "Top Tracks"))
        self.limit_label.setVisible(show_limit)
        self.spn_limit.setVisible(show_limit)
        


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

        tr  = self.time_range_dict[self.cmb_range.currentText()]
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
        elif view.startswith("Top Genres"):
            self.status.setText("Loading genres…")
            self._worker = GenreCardsWorker(self.sp, time_range=tr, limit=3)
            self._thread = start_worker(self, self._worker, self._worker.run)
            self._worker.done.connect(self.on_genre_cards_done)
            self._worker.done.connect(self._thread.quit)
            self._worker.done.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.start()
        elif view.startswith("Top Tracks"):
            self.status.setText("Loading tracks…")
            self._worker = TopTracksWorker(self.sp, time_range=tr, limit=lim)
            self._thread = start_worker(self, self._worker, self._worker.run)
            self._worker.done.connect(self.on_track_cards_done)
            self._worker.done.connect(self._thread.quit)
            self._worker.done.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.start()

        elif view.startswith("Recommend More"):
            
            self.status.setText("Thinking...")
            pop = 'high'   # 'low'/'med'/'high'
            self._worker = RecommendArtistTrackWorker(self.sp, popularity=pop)
            self._thread = start_worker(self, self._worker, self._worker.run)

            self._worker.done.connect(self.on_rec_cards_done)
            self._worker.finished.connect(self._thread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)

            self._thread.start()

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

    def on_genre_cards_done(self, items, error):
        if error:
            self.status.setText("Error loading genres")
            QMessageBox.critical(self, "API Error", str(error))
            return
        if not items:
            self.status.setText("No genres found")
            return

        self.grid.setColumnStretch(0, 1)
        for r, g in enumerate(items):
            if isinstance(g, dict):
                genre = g.get("genre", "Unknown")
                url = g.get("image_url")
            else:  # string fallback
                genre, url = str(g), None

            card = GenreBannerCard(genre, url, height=150)
            self.grid.addWidget(card, r, 0)

        self.status.setText(f"Loaded {len(items)} genres")

    @Slot(list, object)
    def on_track_cards_done(self, items: List[Dict[str, Optional[str]]], error):
        if error:
            self.status.setText("Error loading tracks")
            QMessageBox.critical(self, "API Error", str(error))
            return
        if not items:
            self.status.setText("No tracks found")
            return

        cols = 3
        for i, t in enumerate(items):
            r, c = divmod(i, cols)
            card = TrackCard(t.get("artist", "Unknown"), t.get("track", "Unknown"), t.get("image_url"))
            self.grid.addWidget(card, r, c)

        self.status.setText(f"Loaded {len(items)} tracks")

    @Slot(dict, object)
    def on_rec_cards_done(self, payload, error):
        if error:
            self.status.setText("Error loading recs")
            QMessageBox.critical(self, "Recommendations Error", str(error))
            return
        if not payload or "recs" not in payload or "photos" not in payload:
            self.status.setText("No recs found")
            return

        
        recs   = payload["recs"]     # {genre: {artist: [tracks...]}}
        photos = payload["photos"]   # {artist: url}
        links = payload["links"]     # {track_title: url}
        genres = list(recs.keys())[:3]  # preserve order


        for i, genre in enumerate(genres):
            header_row = i * 2
            cards_row  = header_row + 1

            
            lbl = QLabel(str(genre))
            f = QFont()
            f.setPointSize(20)
            f.setBold(True)
            lbl.setFont(f)
            lbl.setStyleSheet("padding-left: 12px;")
            self.grid.addWidget(lbl, header_row, 0, 1, 3, alignment=Qt.AlignLeft)  

            for c, artist in enumerate(list(recs[genre].keys())[:3]):
                img_url = photos.get(artist)
                tracks  = recs[genre][artist]

                card = RecCard(artist=artist, image_url=img_url, genre=genre, tracks=tracks, track_urls= links)
                card.clicked.connect(self.show_rec_modal)
                self.grid.addWidget(card, cards_row, c)

        self.status.setText("Loaded 9 recommended artists")

    def show_rec_modal(self, artist: str, tracks: list[str], track_urls, image_url: str | None, genre: str | None = None):
        
        dlg = RecModal(artist= artist, tracks= tracks, track_urls= track_urls,image_url= image_url, parent= self)
        dlg.exec()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        self._view.setGeometry(0, 0, size.width(), size.height())
        self._video_item.setSize(size)
        self._scene.setSceneRect(QRectF(0, 0, size.width(), size.height()))