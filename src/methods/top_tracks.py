from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter

import random
import json

from pathlib import Path

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