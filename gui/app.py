#-------------------------------------
#Author: Quinn Olney

#What it does: Entry point for app
#-------------------------------------
import os, sys, threading
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.shell import Shell
from gui.widgets.autoreloader import start_dev_reloader
import time
from PySide6.QtGui import QFontDatabase

try:
    from watchfiles import watch
    HAVE_WATCHFILES = True
except ImportError:
    HAVE_WATCHFILES = False

APP_DIR = Path(__file__).resolve().parent
PAGES_DIR = APP_DIR / "pages"


def load_fonts():
    font_dir = Path(__file__).parent / "pages" / "fonts"
    for font_file in font_dir.glob("*.ttf"):
        font_id = QFontDatabase.addApplicationFont(str(font_file))
        if font_id == -1:
            pass
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
            

def _load_stylesheet() -> str:
    qss = PAGES_DIR / "style.qss"
    return qss.read_text(encoding="utf-8") if qss.exists() else ""

def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setStyleSheet(_load_stylesheet())
    w = Shell()
    w.resize(700, 800)
    app.setStyleSheet(_load_stylesheet())
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # Only enable during dev; disable with APP_AUTORELOAD=0
    '''
    if os.environ.get("APP_AUTORELOAD", "1") == "1":
        start_dev_reloader()

    '''
    main()
