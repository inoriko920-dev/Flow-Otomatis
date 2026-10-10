"""Capture real empty Workspace/Hasil in the main Windows Qt shell."""

from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication, QPushButton

from capture_credit_uix import _ensure_readable_capture_font
from flow_otomatis.presentation.main_window import MainWindow


class EmptyProjectLibrary:
    def scan_recent(self):
        return SimpleNamespace(workspaces=(), issues=())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()
    if args.width < 1180 or args.height < 700:
        parser.error("Viewport is below the supported desktop layout")
    args.destination.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _ensure_readable_capture_font()

    window = MainWindow(
        project_library_service=EmptyProjectLibrary(),
        episode_import_service=SimpleNamespace(),
    )
    window.configure_production_shell()
    window.resize(args.width, args.height)
    window.show()

    for route in ("Workspace", "Hasil"):
        window._open_navigation_item(route)
        app.processEvents()
        page = window._content_layout.itemAt(0).widget()
        if page is None or page.objectName() != f"RealEmpty{route}":
            raise RuntimeError(f"Real empty route not mounted: {route}")
        if window._connection_badge.text() != "●  Mode Lokal":
            raise RuntimeError(f"False Online badge in empty {route}")
        if not window._right_host.isHidden():
            raise RuntimeError(f"Fake AI panel visible in empty {route}")
        for button_name in ("RealEmptyHome", "RealEmptyImport"):
            button = page.findChild(QPushButton, button_name)
            if button is None or not button.isVisible() or not button.isEnabled():
                raise RuntimeError(f"Empty {route} button missing/unusable: {button_name}")
        output = args.destination / f"EMPTY-{route.upper()}.png"
        if not window.grab().save(str(output)):
            raise RuntimeError(f"Cannot render empty {route} screenshot")
    window.close()

    if len(tuple(args.destination.glob("EMPTY-*.png"))) != 2:
        raise RuntimeError("Both empty Workspace and Hasil screenshot files are required")
    print(f"Verified 2 real project-free pages at {args.width}x{args.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
