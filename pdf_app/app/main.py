from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pdf_app import __version__
from pdf_app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PDF App MVP")
    app.setApplicationDisplayName("PDF App MVP")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PDF App MVP")
    app.setOrganizationDomain("local.pdf-app-mvp")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
