'''
Author: Quinn (Gigawttz)

What it Does: Creates the spotify client Obj that is then referenced
and passed through later spotify API methods
'''

from .spotify_client import get_spotify_client  # type: ignore
from .user_data import (
    get_user_profile, top_tracks, top_artists, genre_breakdown, audio_features_for_tracks, artist_recommendation 
)

def main():
    sp = get_spotify_client()




if __name__ == '__main__':
    sp = get_spotify_client()

    #checks everything works
    me = sp.me()
    print(f"✅ Auth OK. Hello {me.get('display_name')} (id={me.get('id')})")
    print(top_artists(sp,limit = 5, time_range = "long_term"))
    print(genre_breakdown(sp, limit = 20, time_range = "long_term"))
   