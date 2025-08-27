import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI","http://127.0.0.1:8080/callback")

SCOPES = os.getenv(
    "SPOTIFY_SCOPES",
    "user-top-read user-read-recently-played user-read-private playlist-read-private"
)