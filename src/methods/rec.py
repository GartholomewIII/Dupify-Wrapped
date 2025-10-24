'''
Author: Quinn (gigawttz)

What it does: reccomends artist and tracks based on the users top genres and listening habits
Flow: genre_breakdown -> genre_artist_track -> get_artist_photos
'''
from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter

import random
import json
from src.spotify_client import get_spotify_client
from pathlib import Path
from .top_genre import genre_breakdown


def get_recent_artists(sp, limit):
    recent_tracks= sp.current_user_recently_played(limit= limit)

    
    
    artists= []

    for item in recent_tracks.get("items", []):
        track = item.get("track") or {}
        names = [a.get("name") for a in (track.get("artists") or []) if a.get("name")]
        if names:
            artists.append(names)
    #because of features, lists can be nested
    clean_arr = []
    for i in artists:
        for j in i:
            clean_arr.append(j)

    return set(clean_arr) #removes duplicates
    


def get_artist_by_genre(sp, genre, limit, popularity, offset= 0):
    '''
    popularity
    low= 0-25
    med= 25-50
    high= 50-100
    '''


    if popularity == 'high':
        offset= random.randrange(0, 20)
    elif popularity == 'med':
        offset= random.randrange(0, 20)
    else:
        offset= random.randrange(0, 20)

    artists = []

    while len(artists) < limit:




        res = sp.search(
            q=str(genre),
            type="artist",
            limit= limit,
            offset=offset,
            market= "US",
        )
        items = res.get('artists')
        

        page = (res.get("artists") or res.get("tracks") or {})
        entries = page.get("items", []) or []
        if not entries:  # no more results
            break

        for i in items['items']:
            pop = i.get('popularity', 0)
            if len(artists) < limit:
                if popularity == 'low' and (pop>= 0 and pop< 50):
                    artists.append(i['name'])

                elif popularity == 'med' and (pop>= 50 and pop< 70):
                    artists.append(i['name'])
                
                elif popularity == 'high' and (pop>= 70):

                    artists.append(i['name'])

        offset += page.get("limit", len(entries))  # advance by page size actually returned
        if not page.get("next") or len(entries) < page.get("limit", 50):
            break

        if offset >= 800:
            return artists
    
    return artists


def get_artist_rec(sp, genre, num_of_artists, popularity):
    '''
    Limit calls of artists to MAX 5, lot of nested loops
    
    returns an arr of artist recs
    
    TO DO: IMPLIMENT A RANDOMIZER FUNCTION
    '''
    recent_listened = get_recent_artists(sp, limit=50)  # returns arr of listened to artists
    rec_tracks = []
    offset_num = 0

    while len(rec_tracks) < num_of_artists:
        artist_by_genre = get_artist_by_genre(
            sp, genre=genre, limit=10, offset=offset_num, popularity=popularity
        )  # set limit to 10 to avoid heavy compute strain
        for i in artist_by_genre:
            if len(set(rec_tracks)) == num_of_artists:
                return list(set(rec_tracks))
            elif i not in recent_listened:
                rec_tracks.append(i)

        offset_num += 1

    return list(set(rec_tracks))

def track_and_artist(sp, genre, num_of_artists, popularity):
    # {'place': 'missoula}
    artist_track = {}
    
    artists = get_artist_rec(sp, 
    genre= genre, 
    num_of_artists= num_of_artists, 
    popularity= popularity)
    
    for i in artists:
        artist_track[i] = []

    offset= 0

    for i in range(len(artists)):
        artist_data= sp.search(
            q= str(artists[i]),
            type= 'track',
            limit= 3,
            offset= offset,
            market= 'US'
        )
        page = (artist_data.get("artists") or artist_data.get("tracks") or {})
        entries = page.get("items", []) or []
        if not entries:  # no more results
            break

        temp = []
        while len(temp) != 3:
            
            for k in range(3):
                if len(temp) == 3:
                    break
                try:
                    if artist_data['tracks']['items'][k]['artists'][0]['name'] == artists[i]:
                        temp.append(artist_data['tracks']['items'][k]['name'])
                except IndexError:
                    continue
                
            if len(temp) < 3:
                offset += page.get("limit", len(entries))  # advance by page size actually returned
                if not page.get("next") or len(entries) < page.get("limit", 50):
                    break

                artist_data= sp.search(
                    q= str(artists[i]),
                    type= 'track',
                    limit= 3,
                    offset= offset,
                    market= 'US'
                )
                
                page = (artist_data.get("artists") or artist_data.get("tracks") or {})
                entries = page.get("items", []) or []
                if not entries:  # no more results
                    break
            
            elif len(temp) == 3:
                break

        artist_track[artists[i]] = temp
        offset= 0

    return artist_track 

def get_artist_photos(sp, genre_artist_track):


    out= {}

    for outer_key, inner_dict in genre_artist_track.items():
        for name in inner_dict:
            # Search a few candidates for this name
            res = sp.search(q=f'artist:"{name}"', type="artist", limit=5)
            items = (res.get("artists") or {}).get("items") or []
            if not items:
                out[name] = None
                continue

            # Pick best match: exact name (case-insensitive) else most popular
            best = next((a for a in items if (a.get("name","").lower() == name.lower())), None)
            if best is None:
                best = max(items, key=lambda a: a.get("popularity", 0))

            images = best.get("images") or []
            if not images:
                out[name] = None
                continue

            # Prefer square images, closest to target_size; else first available
            squares = [im for im in images if im.get("width") and im.get("height") and im["width"] == im["height"]]
            if squares:
                squares.sort(key=lambda im: abs(im["width"] - 320))
                out[name] = squares[0].get("url")
            else:
                out[name] = images[0].get("url")

    return out

def genre_artist_track(sp, genres, popularity, num_of_artists= 3 ):
    out = {}

    for i in genres:
        out[i]= track_and_artist(sp, genre= i, num_of_artists= num_of_artists, popularity= popularity)

    return out

def get_track_link(sp, artist, track, market= 'US'):

    # 1) strict search: quoted artist + track
    q = f'track:"{track}" artist:"{artist}"'
    res = sp.search(q=q, type="track", limit=10, market=market)
    items = (res.get("tracks") or {}).get("items") or []

    # 2) fallback: looser search if strict returns nothing
    if not items:
        q = f'{track} {artist}'
        res = sp.search(q=q, type="track", limit=10, market=market)
        items = (res.get("tracks") or {}).get("items") or []
        if not items:
            return None

    # 3) pick best match (exact name/artist first, then popularity)
    tl = track.lower()
    al = artist.lower()

    def score(t):
        tname = (t.get("name") or "").lower()
        anames = [a.get("name","").lower() for a in t.get("artists") or []]
        s = 0
        if tname == tl: s += 2
        if al in anames: s += 2
        if tl in tname: s += 1
        if any(al in a for a in anames): s += 1
        return (s, t.get("popularity", 0))

    best = max(items, key=score)
    return (best.get("external_urls") or {}).get("spotify") or (
        f'https://open.spotify.com/track/{best["id"]}' if best.get("id") else None
)


if __name__ == '__main__':
    sp = get_spotify_client()

    genres = genre_breakdown(sp, limit= 20, time_range= 'long_term', offset = 0)
    genre_artist_track = genre_artist_track(sp, genres= genres, popularity= 'high')
    artist_photos = get_artist_photos(sp, genre_artist_track= genre_artist_track)

    print(genre_artist_track)
    print(artist_photos)
    