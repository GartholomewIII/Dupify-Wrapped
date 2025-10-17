from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter
import random
import json

from pathlib import Path

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