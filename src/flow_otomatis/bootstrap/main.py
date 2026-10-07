"""Foundation application entry point.

STEP 08 initializes the chosen Qt runtime and portable paths but deliberately
does not implement product screens. Frozen UI implementation starts later.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from flow_otomatis.infrastructure.filesystem import PathService


def main() -> int:
    """Initialize the foundation runtime and exit successfully."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    app.setApplicationName("Flow-Otomatis")
    PathService.discover()
    return 0
