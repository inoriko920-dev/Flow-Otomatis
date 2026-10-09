"""Launch the E12-02 Qt preview independently from the production application."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from flow_otomatis.presentation.credit_uix_preview import CreditUixDialog


def main() -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    preview = CreditUixDialog()
    preview.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
