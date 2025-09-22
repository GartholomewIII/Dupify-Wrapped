import os, sys, threading
import time
from pathlib import Path

try:
    from watchfiles import watch
    HAVE_WATCHFILES = True
except ImportError:
    HAVE_WATCHFILES = False

APP_DIR = Path(__file__).resolve().parents[1]  
PAGES_DIR = APP_DIR / "pages"

FILES_TO_WATCH = [
    PAGES_DIR / "login_page.py",
    PAGES_DIR / "main_page.py",
    PAGES_DIR / "style.qss",  
]


def _restart_process():
    """Restart preserving the original invocation (module vs script)."""
    # If we were started as a module (python -m gui.app), __spec__ is set.
    module_name = getattr(sys.modules.get("__main__"), "__spec__", None)
    if module_name and module_name.name:
        # Preserve module-style launch
        args = [sys.executable, "-m", module_name.name, *sys.argv[1:]]
    else:
        # Script-style launch
        script = sys.argv[0]
        args = [sys.executable, script, *sys.argv[1:]]

    print(f"[reloader] exec: {' '.join(args)}")
    os.execv(sys.executable, args)

def start_dev_reloader():
    if not HAVE_WATCHFILES:
        print("[reloader] Tip: pip install watchfiles to enable auto-reload")
        return

    watch_list = []
    for p in FILES_TO_WATCH:
        if p.exists():
            watch_list.append(str(p))
        else:
            print(f"[reloader] Skipping missing: {p}")
    if not watch_list:
        print("[reloader] Nothing to watch; disable autoreload.")
        return

    def _worker():
        print("[reloader] Watching:")
        for f in watch_list:
            print("  •", f)
        for changes in watch(*watch_list, debounce=500):
            # Any change to these files triggers a restart
            for change_type, changed in changes:
                print(f"[reloader] {change_type.name}: {changed}")
            print("🔁 Code/style change — restarting…")
            time.sleep(3)
            _restart_process()

    threading.Thread(target=_worker, daemon=True).start()