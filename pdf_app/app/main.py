from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pdf_app import __version__
from pdf_app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MyLeaflet")
    app.setApplicationDisplayName("MyLeaflet - Mini Launch v0.2")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("MyLeaflet")
    app.setOrganizationDomain("local.myleaflet")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
