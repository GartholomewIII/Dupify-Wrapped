from typing import Literal, Dict, Any, List, Optional, Union
from collections import Counter

import random
import json

from pathlib import Path

#returns key value pair of users profile info
def get_user_profile(sp: "spotipy.Spotify") -> Dict[str, Any]:
    me = sp.me()
    return {
        "display_name": me.get("display_name"),
        "id": me.get("id"),
        "product": me.get("product"),  # free/premium
        "country": me.get("country")
    }