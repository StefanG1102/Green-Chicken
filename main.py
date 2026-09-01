"""
Projektname
-----------
Kurze Beschreibung des Programms.

Autor: Dein Name
Universität: Name der Universität
Veranstaltung: z. B. Seminar XY
Datum: September 2026
"""

import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("Image Analyzer")
    app.setOrganizationName("ImageAnalyzer")

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
