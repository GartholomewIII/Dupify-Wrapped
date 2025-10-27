'''
Author: Quinn (Gigawttz)

What it Does: loads spotify API credentials
'''
import os, json
from pathlib import Path

try:
    from platformdirs import user_config_dir
except ImportError:
    from appdirs import user_config_dir

APP_NAME = "Dupify"
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_PATH = CONFIG_DIR / "config.json"

def _load_cfg():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_spotify_client_id():
    cid = os.getenv("SPOTIFY_CLIENT_ID")
    if not cid and os.getenv("APP_ENV") != "production":
        try:
            from dotenv import load_dotenv
            load_dotenv()
            cid = os.getenv("SPOTIFY_CLIENT_ID")
        except Exception:
            pass
    if not cid:
        cid = _load_cfg().get("SPOTIFY_CLIENT_ID", "")
    return cid

def get_redirect_uri():
    uri = os.getenv("SPOTIFY_REDIRECT_URI")
    if not uri and os.getenv("APP_ENV") != "production":
        try:
            from dotenv import load_dotenv
            load_dotenv()
            uri = os.getenv("SPOTIFY_REDIRECT_URI")
        except Exception:
            pass
    if not uri:
        uri = _load_cfg().get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    return uri

def get_scopes():
    scopes = os.getenv("SPOTIFY_SCOPES")
    if not scopes and os.getenv("APP_ENV") != "production":
        try:
            from dotenv import load_dotenv
            load_dotenv()
            scopes = os.getenv("SPOTIFY_SCOPES")
        except Exception:
            pass
    if not scopes:
        scopes = _load_cfg().get("SPOTIFY_SCOPES", "user-read-recently-played playlist-read-private")
    return scopes
