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
from src.methods.rec import genre_breakdown, genre_artist_track, get_artist_photos, get_track_link



class LoginWorker(QObject):
    done = Signal(object, object)  # (sp, error)

    @Slot()
    def run(self):
        try:
            sp = get_spotify_client()
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


class RecommendArtistTrackWorker(QObject):
    
    done = Signal(dict, object)   # payload, error
    error = Signal(str)
    finished = Signal()

    def __init__(self, sp, popularity, time_range='long_term', limit=20):
        super().__init__()
        self.sp = sp
        self.time_range = time_range
        self.limit = limit
        self.popularity = popularity

    @Slot()
    def run(self):
        try:
            genres = genre_breakdown(self.sp, limit=self.limit, time_range=self.time_range)
            recs = genre_artist_track(self.sp, genres=genres, popularity=self.popularity)  # {genre:{artist:[...]}}

            links = {}

            for genre in genres[:3]:                                  # your 3 genres
                for artist, tracks in list(recs.get(genre, {}).items())[:3]:  # 3 artists per genre
                    for track in tracks:
                        url = get_track_link(self.sp, artist, track)
                        if not url:
                            continue
                        key = track
                        # avoid collisions if two different artists have a track with same title
                        if key in links:
                            key = f"{track} — {artist}"
                        links[key] = url


            photos = get_artist_photos(self.sp, genre_artist_track=recs)  # {artist: url}
            
            payload = {"recs": recs, "photos": photos, "links": links}
            self.done.emit(payload, None)
        except Exception as e:
            # either use the dedicated error signal OR pass error via done; here we pass via done:
            self.done.emit({}, e)
        finally:
            self.finished.emit()

    


def start_worker(widget_parent, worker: QObject, started_slot):
    """Utility to spin up a worker on its own QThread and wire cleanup."""
    t = QThread(widget_parent)
    worker.moveToThread(t)
    t.started.connect(started_slot)
    # caller should connect worker.done to slots, and to t.quit/worker.deleteLater
    return t