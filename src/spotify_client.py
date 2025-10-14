'''
Author: Quinn (Gigawttz)

What it Does: API call
'''


import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES

def get_spotify_client(cache_path: str = '.cache') -> spotipy.Spotify:
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=cache_path,
        show_dialog=False
    )
    return spotipy.Spotify(auth_manager=auth_manager)




#------------- MAKES THE API CALL -------------