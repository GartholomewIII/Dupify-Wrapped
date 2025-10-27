#-------------------------------------
#Author: Quinn Olney

#What it does: Entry point for app
#-------------------------------------

# app.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import QFile, QIODevice, QDir
import gui.resources_rc
from gui.shell import Shell

def load_fonts():
    d = QDir(":/pages/fonts")
    for name in d.entryList(["*.ttf", "*.otf"], QDir.Files):
        QFontDatabase.addApplicationFont(f":/pages/fonts/{name}")

def load_qss() -> str:
    f = QFile(":/pages/style.qss")
    if f.open(QIODevice.ReadOnly | QIODevice.Text):
        return bytes(f.readAll()).decode("utf-8")
    return ""

def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setStyleSheet(load_qss())
    w = Shell()
    w.resize(700, 800)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

