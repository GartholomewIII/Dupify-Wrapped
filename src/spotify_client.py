'''
Author: Quinn (Gigawttz)

What it Does: API call
'''


import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES

CACHE_PATH = '.cache'
DAILY_SECONDS = 24 * 60 * 60

def get_spotify_client(force_daily_reauth: bool = True) -> spotipy.Spotify:

    show_dialog = False

    if force_daily_reauth:
        try:
            mtime = os.path.getmtime(CACHE_PATH)
            if time.time() - mtime > DAILY_SECONDS:
                os.remove(CACHE_PATH)
                show_dialog = True

        except FileNotFoundError:
            show_dialog = True
        

    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_handler=CacheFileHandler(cache_path= CACHE_PATH),  # <- no persisted cache
        show_dialog= show_dialog 
    )
    return spotipy.Spotify(auth_manager=auth_manager)


#------------- MAKES THE API CALL -------------