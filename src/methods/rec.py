from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter

import random
import json

from pathlib import Path



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
        offset= random.randrange(0, 40)
    elif popularity == 'med':
        offset= random.randrange(100, 190)
    else:
        offset= random.randrange(400, 480)

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
        



        for i in items['items']:
            pop = i.get('popularity', 0)
            if len(artists) < limit:
                if popularity == 'low' and (pop>= 0 and pop< 25):
                    artists.append(i['name'])

                elif popularity == 'med' and (pop>= 25 and pop< 50):
                    artists.append(i['name'])
                
                elif popularity == 'high' and (pop>= 50):

                    artists.append(i['name'])
        offset+= 10
    
    return artists


def get_artist_rec(sp, genre, num_of_artists, popularity):
    '''
    Limit calls of artists to MAX 5, lot of nested loops
    
    returns an arr of artist recs
    
    TO DO: IMPLIMENT A RANDOMIZER FUNCTION
    '''
    recent_listened = get_recent_artists(sp, limit= 50) #returns arr of listened to artists
    

    rec_tracks = []

    offset_num = 50

    while len(rec_tracks) < num_of_artists:
        artist_by_genre = get_artist_by_genre(sp, genre= genre, limit= 10, offset= offset_num, popularity= popularity) #set limit to 10 to avoid heavy compute strain
        for i in artist_by_genre:
            if len(rec_tracks) == num_of_artists:
                return rec_tracks
            elif i not in recent_listened:
                rec_tracks.append(i)
            
        

        offset_num += 10


def track_and_artist(sp, artists):
    # {'place': 'missoula}
    artist_track = {}

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
                
            if len(temp) != 3:
                offset+= 3
                artist_data= sp.search(
                    q= str(artists[i]),
                    type= 'track',
                    limit= 3,
                    offset= offset,
                    market= 'US'
                )

        artist_track[artists[i]] = temp
        offset= 0

    return artist_track 

def get_track_photos(sp, artists_songs):
    pass