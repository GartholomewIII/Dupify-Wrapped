'''
Author: Quinn (Gigawttz)

What it Does: API call
'''


import os, certifi, spotipy
from pathlib import Path
try:
    from platformdirs import user_cache_dir
except ImportError:
    from appdirs import user_cache_dir
from spotipy.oauth2 import SpotifyPKCE
from .config import get_spotify_client_id, get_redirect_uri, get_scopes, APP_NAME

os.environ.setdefault("SSL_CERT_FILE", certifi.where())

CACHE_DIR = Path(user_cache_dir(APP_NAME))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_PATH = str(CACHE_DIR / ".spotipy_cache")

def get_spotify_client():
    client_id = get_spotify_client_id()
    if not client_id:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID")
    auth_manager = SpotifyPKCE(
        client_id=client_id,
        redirect_uri=get_redirect_uri(),
        scope=get_scopes(),
        cache_path=CACHE_PATH,
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth_manager)



#------------- MAKES THE API CALL -------------