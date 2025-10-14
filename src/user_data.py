'''
Author: Quinn (Gigawttz)

What it Does: Calls the Spotify API methods and retrieves user data that is going to be processed and displayed in the gui/ directory
'''
'''
TO DO: CLEAN UP UNUSED FUNCTIONS
'''

from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter
from .spotify_client import get_spotify_client
import random
import json

from pathlib import Path

GENRE_MAP_PATH = Path(__file__).parent / "data" / "genre_norm.json"

with GENRE_MAP_PATH.open(encoding="utf-8") as f:
    _CATEGORY_KEYWORDS = json.load(f)


#returns key value pair of users profile info
def get_user_profile(sp: "spotipy.Spotify") -> Dict[str, Any]:
    me = sp.me()
    return {
        "display_name": me.get("display_name"),
        "id": me.get("id"),
        "product": me.get("product"),  # free/premium
        "country": me.get("country")
    }

def top_tracks_map(sp, limit: int, time_range: str) -> Dict[str, str]:

    raw = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    out: Dict[str, str] = {}
    for t in raw.get("items", []):
        track = t.get("name") or "Unknown"
        artists = [a.get("name") for a in t.get("artists", []) if a.get("name")]
        artist = " & ".join(artists) if artists else "Unknown"
        if artist not in out:  # avoid overwriting if same artist appears multiple times
            out[artist] = track
    return out

def top_tracks_items(sp, limit: int, time_range: str) -> List[Dict[str, Optional[str]]]:
    raw = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    items: List[Dict[str, Optional[str]]] = []

    for t in raw.get("items", []):
        track = t.get("name") or "Unknown"
        artists = [a.get("name") for a in t.get("artists", []) if a.get("name")]
        artist = " & ".join(artists) if artists else "Unknown"
        images = (t.get("album") or {}).get("images", [])
        url = None

        for img in images:
            if img.get("height") == img.get("width"):
                url = img.get("url")
                break
        if not url and images:
            url = images[0].get("url")
        #returns a list of dicts with len of 3
        items.append({"artist": artist, "track": track, "image_url": url})
    return items

    


#returns a list of the users most listened to artists
#sp (spotify obj), limit = how many artists (max == 20), time_range ('short_term', 'medium_term, 'long_term')
def top_artists(sp, limit, time_range , offset=0) -> Dict[str, Any]:
    raw_data = sp.current_user_top_artists(limit= limit, offset= offset, time_range= time_range)

    artists = []

    for i in raw_data['items']:
        artists.append(i['name'])

    return artists

#fetches top artists and their respective info (name, id #, images, genres, popularity)
def _top_artist_data(sp, limit, time_range, offset= 0):
    raw_data = sp.current_user_top_artists(limit= limit, offset= offset, time_range= time_range)
    artists = []

    for item in raw_data["items"]:
        artists.append({
            "id": item['id'],
            "name": item['name'],
            'images': item.get('images', []),
            'genres': item.get('genres', []),
            'popularity': item.get('popularity', None)
            })
    return artists
    
#returns a list of top 3 genres with a weighted algorithm 
def genre_breakdown(sp, limit, time_range, offset = 0) -> Dict[str, Any]:
    raw_data = sp.current_user_top_artists(20, offset= offset, time_range= time_range)
    
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

def get_photos(sp, limit, time_range, offset = 0 ):
    artist_data = _top_artist_data(sp= sp, limit= limit, time_range= time_range)

    urls = []
    for artist in artist_data:
        chosen = None
        images = artist.get("images", [])

        for img in images:
            if img.get("height") == img.get("width"):
                chosen = img["url"]
                break

        if not chosen and images:
            chosen = images[0]["url"]

        urls.append(chosen or None)
    return urls

def _normalize_genre_text(s):
    return (s or "").lower().replace("-", " ").replace("&", "and").strip()


def _fetch_browse_categories(sp):
    categories = []
    offset = 0
    while True:
        r = sp.categories(limit=50, offset=offset, country="US")
        items = r.get("categories", {}).get("items", [])
        if not items:
            break
        for it in items:
            icons = it.get("icons") or []
            if icons:
                categories.append({"name": it.get("name"), "image_url": icons[0].get("url")})
        if len(items) < 50:
            break
        offset += 50
    return categories

'''
_CATEGORY_KEYWORDS = {
    "rap": "Hip-Hop",
    "drill": "Hip-Hop",
    "trap": "Hip-Hop",
    "pluggnb": "Hip-Hop",
    "plug": "Hip-Hop",
    "hip": "Hip-Hop",
    "hop": "Hip-Hop",
    "rnb": "R&B",
    "r&b": "R&B",
    "soul": "R&B",
    "pop": "Pop",
    "hyperpop": "Pop",
    "indie": "Indie",
    "alt": "Indie",
    "rock": "Rock",
    "metal": "Metal",
    "country": "Country",
    "jazz": "Jazz",
    "blues": "Blues",
    "edm": "Dance/Electronic",
    "dance": "Dance/Electronic",
    "electronic": "Dance/Electronic",
    "house": "Dance/Electronic",
    "techno": "Dance/Electronic",
    "trance": "Dance/Electronic",
    "kpop": "K-Pop",
    "latin": "Latin",
    "reggaeton": "Latin",
    "classical": "Classical",
    "folk": "Folk & Acoustic",
    "reggae": "Reggae",
}
'''

def _best_category_image(genre, categories):
    import difflib
    g = _normalize_genre_text(genre)
    tokens = g.split()

    
    target = None
    for t in tokens:
        if t in _CATEGORY_KEYWORDS:
            target = _CATEGORY_KEYWORDS[t]
            break
    if target:
        tnorm = _normalize_genre_text(target)
        for c in categories:
            if _normalize_genre_text(c["name"]) == tnorm:
                return c["image_url"]
        # fall back to fuzzy against the target label
        best = None
        best_score = 0.0
        for c in categories:
            score = difflib.SequenceMatcher(None, tnorm, _normalize_genre_text(c["name"])).ratio()
            if score > best_score:
                best_score, best = score, c["image_url"]
        if best:
            return best

    # 2) fuzzy match the original genre to category names
    best = None
    best_score = 0.0
    for c in categories:
        score = difflib.SequenceMatcher(None, g, _normalize_genre_text(c["name"])).ratio()
        if score > best_score:
            best_score, best = score, c["image_url"]
    return best if best_score >= 0.5 else None  # slightly lower threshold


def _representative_artist_images_for_genre(sp, genre, time_range):
    g = _normalize_genre_text(genre)
    gtokens = set(g.split())
    items = sp.current_user_top_artists(limit=50, time_range=time_range).get("items", [])

    def pick_image(artist):
        images = artist.get("images") or []
        for img in images:
            if img.get("height") == img.get("width"):
                return img.get("url")
        if images:
            return images[0].get("url")
        return None

    candidates = []
    for a in items:
        genres = [_normalize_genre_text(x) for x in (a.get("genres") or [])]
        if g in genres:
            url = pick_image(a)
            if url:
                candidates.append(url)
    if not candidates:
        for a in items:
            genres_joined = " ".join(_normalize_genre_text(x) for x in (a.get("genres") or []))
            if gtokens & set(genres_joined.split()):
                url = pick_image(a)
                if url:
                    candidates.append(url)
    if not candidates:
        for a in items:
            url = pick_image(a)
            if url:
                candidates.append(url)
    return candidates


def get_genre_banners(sp, time_range="medium_term", limit=3):
    top3 = genre_breakdown(sp, limit=limit, time_range=time_range)
    cats = _fetch_browse_categories(sp)
    out = []
    seen = set()
    for g in top3[:limit]:
        url = None
        for cand in _representative_artist_images_for_genre(sp, g, time_range):
            if cand not in seen:
                url = cand
                break
        if not url:
            url = _best_category_image(g, cats)
        if url:
            seen.add(url)
        out.append({"genre": g, "image_url": url})
        
    return out

def get_top_genre_artists(sp, genre, total: int = 100) -> List[Dict[str, Any]]:
    """
    Returns up to `total` artist objects for a given genre,
    sorted by artist popularity (desc).
    """
    q = f'genre:"{_CATEGORY_KEYWORDS[genre]}"'            # quotes handle spaces in genre
    limit = 50                        # Spotify Search max per page = 50
    collected: List[Dict[str, Any]] = []

    # page through search results until we hit `total` or run out
    for offset in range(0, total, limit):
        res = sp.search(q=q, type="artist", limit=min(limit, total - offset), offset=offset)
        items = (res.get("artists", {}) or {}).get("items", []) or []
        if not items:
            break
        collected.extend(items)

        # if fewer than requested came back, no more pages
        if len(items) < min(limit, total - offset):
            break

    # de-dupe by id
    by_id = {}
    for a in collected:
        aid = a.get("id")
        if aid and aid not in by_id:
            by_id[aid] = a

    # rank by popularity (0–100; higher = more popular)
    ranked = sorted(by_id.values(), key=lambda a: a.get("popularity", 0), reverse=True)
    
    top_100_artist = []

    for i in ranked[:total]:
        top_100_artist.append(i['name'])

    return top_100_artist

'''
def get_artist_rec(sp, time_range= "long_term", limit= 20):
    top_3 = genre_breakdown(sp, time_range= time_range, limit= limit)

    seen_artists= []
    for i in top_3:
        #fetch top 100 artists in genre
        artists = pass

        artist= random.choice(artists)
        
        if artist not in seen_artist

'''
if __name__ == '__main__':
    sp = get_spotify_client()

    print(get_top_genre_artists(sp, genre= 'pop'))