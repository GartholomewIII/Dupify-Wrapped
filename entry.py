import os, sys
if getattr(sys, "frozen", False):
    os.environ.setdefault("APP_ENV", "production")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gui.app import main

if __name__ == "__main__":
    import os, sys
    if getattr(sys, "frozen", False):
        os.environ.setdefault("APP_ENV", "production")

    main()