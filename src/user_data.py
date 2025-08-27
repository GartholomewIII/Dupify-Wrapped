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


if __name__ == '__main__':
    pass