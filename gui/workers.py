#--------------------------------
#Author: Quinn (Gigawttz)

#What it Does: Holds worker functions that connect the src directory
#to the frontend directory
#--------------------------------

from typing import List, Optional
from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.spotify_client import get_spotify_client

from src.methods.top_artist import top_artists
from src.methods.top_genre import genre_breakdown, get_photos, get_genre_banners
from src.methods.top_tracks import top_tracks_items, top_tracks_map




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


class ArtistCardsWorker(QObject):

    done = Signal(list, object)

    def __init__(self, sp, time_range: str, limit: int):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit

    @Slot()

    def run(self):
        try:
            names: List[str] = top_artists(self.sp, limit= self.limit, time_range= self.time_range)
            urls: List[Optional[str]] = get_photos(self.sp, limit=self.limit, time_range= self.time_range)
            items: List[Dict[str, Optional[str]]] = [
                {"name": n, "image_url": u} for n, u in zip(names, urls)
            ]
            self.done.emit(items, None)
        except Exception as e:
            self.done.emit([], e)

class GenreCardsWorker(QObject):
    done = Signal(list, object)

    def __init__(self, sp, time_range: str, limit: int = 3):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit

    @Slot()
    def run(self):
        try:
            # Primary path: returns [{"genre": "...", "image_url": "..."}]
            items = get_genre_banners(self.sp, time_range=self.time_range, limit=self.limit)

            # If nothing came back (unlikely), degrade gracefully to names only
            if not items:
                genres = genre_breakdown(self.sp, limit=self.limit, time_range=self.time_range)
                items = [{"genre": g, "image_url": None} for g in genres]

            self.done.emit(items, None)

        except Exception as e:
            # Absolute fallback: names only if even banners failed
            try:
                genres = genre_breakdown(self.sp, limit=self.limit, time_range=self.time_range)
                items = [{"genre": g, "image_url": None} for g in genres]
                self.done.emit(items, None)
            except Exception as ee:
                self.done.emit([], ee)

class TopTracksWorker(QObject):
    done = Signal(list, object)

    def __init__(self, sp, time_range, limit):
        super().__init__()

        self.sp = sp
        self.time_range = time_range 
        self.limit = limit


    @Slot()
    def run(self):

        try:
            items = top_tracks_items(self.sp, limit= self.limit, time_range= self.time_range)
            self.done.emit(items, None)
        except Exception as e:
            try:
                m = top_tracks_map(self.sp, limit= self.limit, time_range= time_range)
                items = [{"artist": a, "track": t, "image_url": None} for a, t in m.items]
                self.done.emit(items, None)
            except Exception as e:
                self.done.emit([], ee)
def start_worker(widget_parent, worker: QObject, started_slot):
    """Utility to spin up a worker on its own QThread and wire cleanup."""
    t = QThread(widget_parent)
    worker.moveToThread(t)
    t.started.connect(started_slot)
    # caller should connect worker.done to slots, and to t.quit/worker.deleteLater
    return t