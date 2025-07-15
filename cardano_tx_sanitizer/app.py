"""
Cardano Transaction Sanitizer
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from cardano_tx_sanitizer import __app_name__, __version__
from cardano_tx_sanitizer.gui import MainWindow


def main():
    """
    Main entry point for the Cardano Transaction Sanitizer application.
    """
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setApplicationDisplayName("Cardano Transaction Sanitizer")

    if sys.platform == "darwin":
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
        try:
            import Foundation

            bundle = Foundation.NSBundle.mainBundle()
            if bundle:
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if info:
                    info["CFBundleName"] = __app_name__
                    info["CFBundleDisplayName"] = __app_name__
        except ImportError:
            pass

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
