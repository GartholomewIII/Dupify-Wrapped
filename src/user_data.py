from typing import Literal, Dict, Any, List
import pandas as pd
from collections import Counter


#returns key value pair of users profile info
def get_user_profile(sp: "spotipy.Spotify") -> Dict[str, Any]:
    me = sp.me()
    return {
        "display_name": me.get("display_name"),
        "id": me.get("id"),
        "product": me.get("product"),  # free/premium
        "country": me.get("country")
    }

def top_tracks(sp: "spotipy.Spotify") -> Dict[str,Any]:
    pass


#returns a list of the users most listened to artists
#sp (spotify obj), limit = how many artists (max == 20), time_range ('short_term', 'medium_term, 'long_term')
def top_artists(sp, limit, time_range , offset=0) -> Dict[str, Any]:
    raw_data = sp.current_user_top_artists(limit= limit, offset= offset, time_range= time_range)

    artists = []

    for i in raw_data['items']:
        artists.append(i['name'])

    return artists
    
    
#returns a list of top 3 genres with a weighted algorithm 
def genre_breakdown(sp, limit, time_range, offset = 0) -> Dict[str, Any]:
    raw_data = sp.current_user_top_artists(limit= limit, offset= offset, time_range= time_range)
    
    genres= []
    artists_ranked = []


    for i in raw_data['items']:
        genres.append(i['genres'])
    for i in raw_data['items']:
        artists_ranked.append(i['name'])
    artists_ranked = list(enumerate(artists_ranked))
    
    #item with genre and weight {cloud_rap: 15} 
    #based off top 20 artist, top artist == 20 and it descends

    weighted_genres = {}
    weight = 20
    for items in range(len(genres)):
        for i in range(len(genres[items])): #iterates through each genre for each top artist
            if genres[items][i] not in weighted_genres:

                weighted_genres[genres[items][i]] = weight - items
            
            else:
                weighted_genres[genres[items][i]] += weight - items
    
    sorted_dict = {}
    for w in sorted(weighted_genres, key=weighted_genres.get, reverse=True):
        sorted_dict[w] = weighted_genres[w]

    top_3 = []
    counter = 0
    for keys in sorted_dict:
        top_3.append(keys)
        counter += 1 

        if counter == 3:
            break
    
    return top_3

def get_photos(sp, artist_names: List[str]):
    """
    Given a list of artist names, return a list of image URLs (one per artist).
    The output list is aligned with the input list.

    Each artist is searched by name; we pick the "best" image available.
    If an artist has no images, return None in that slot.
    """

    urls: List[Optional[str]] = []

    for name in artist_names:
        try:
            r = sp.search(q=name, type="artist", limit=1)
            items = r.get("artists", {}).get("items", [])
            if not items:
                urls.append(None)
                continue

            artist = items[0]
            images = artist.get("images", [])

            # Spotify returns images sorted largest → smallest.
            # We'll try to pick a ~300px image for consistency.
            chosen = None
            for img in images:
                w = img.get("width") or 0
                if 200 <= w <= 400:
                    chosen = img["url"]
                    break

            if not chosen and images:
                # fallback: use largest available
                chosen = images[0]["url"]

            urls.append(chosen)
        except Exception:
            urls.append(None)

    return urls

if __name__ == '__main__':
    pass