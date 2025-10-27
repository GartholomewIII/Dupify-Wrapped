# src/config.py
import os, sys, json
from pathlib import Path
try:
    from platformdirs import user_config_dir
except ImportError:
    from appdirs import user_config_dir

APP_NAME = "Dupify"
DEFAULT_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID_HERE"  # <-- put your Client ID here
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"

def _is_frozen(): return getattr(sys, "frozen", False)

def _candidate_config_paths():
    p = [Path(user_config_dir(APP_NAME)) / "config.json"]
    appdata, local = os.getenv("APPDATA"), os.getenv("LOCALAPPDATA")
    if appdata: p.append(Path(appdata)/APP_NAME/"config.json")
    if local:   p.append(Path(local)/APP_NAME/"config.json")
    if _is_frozen(): p.append(Path(sys.executable).parent/"config.json")
    return p

def _load_cfg():
    for path in _candidate_config_paths():
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except: pass
    return {}

def get_spotify_client_id():
    cid = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    if cid: return cid
    cid = (_load_cfg().get("SPOTIFY_CLIENT_ID") or "").strip()
    return cid or DEFAULT_CLIENT_ID

def get_redirect_uri():
    uri = os.getenv("SPOTIFY_REDIRECT_URI", "").strip()
    if not uri:
        uri = (_load_cfg().get("SPOTIFY_REDIRECT_URI") or DEFAULT_REDIRECT_URI).strip()
    return uri

def get_scopes():
    scopes = os.getenv("SPOTIFY_SCOPES", "").strip()
    if not scopes:
        scopes = (_load_cfg().get("SPOTIFY_SCOPES") or "user-read-recently-played playlist-read-private").strip()
    return scopes
