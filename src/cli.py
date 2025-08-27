from .spotify_client import get_spotify_client  # type: ignore
from .user_data import (
    get_user_profile, top_tracks, top_artists, genre_breakdown, audio_features_for_tracks
)

def main():
    sp = get_spotify_client()




if __name__ == '__main__':
    sp = get_spotify_client()

    # 1) Basic identity call (definitive proof auth worked)
    me = sp.me()
    print(f"✅ Auth OK. Hello {me.get('display_name')} (id={me.get('id')})")
    print(top_artists(sp,limit = 5, time_range = "long_term"))
    print(genre_breakdown(sp, limit = 20, time_range = "long_term"))
   