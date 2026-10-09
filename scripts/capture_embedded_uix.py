"""Capture all 22 REAL embedded Qt workspace screens for Windows visual QA.

Unlike the standalone UIX22 test executable, this is the real MainWindow
navigation/content shell with its single sidebar. No Google login or network.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFrame, QLabel

from capture_credit_uix import _ensure_readable_capture_font
from flow_otomatis.presentation.credit_uix_preview import UIX_SCENARIOS
from flow_otomatis.presentation.main_window import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _ensure_readable_capture_font()

    window = MainWindow()
    window.resize(1920, 1080)
    window.show()
    window.open_credit_uix_preview()
    preview = window._active_uix_preview
    if preview is None or window.fixture_code != "REAL_UIX22_PREVIEW":
        raise RuntimeError("UIX22 did not mount inside the real application shell")
    if not preview.findChild(QLabel, "UixDockState"):
        raise RuntimeError("UIX22 lacks its live-state navigation label")
    if not preview.findChild(QFrame, "UixSidebar").isHidden():
        raise RuntimeError("Duplicate offline sidebar visible in real application")
    for scenario in UIX_SCENARIOS:
        preview.set_state(scenario.code)
        app.processEvents()
        output = args.destination / f"{scenario.code}.png"
        if not window.grab().save(str(output)):
            raise RuntimeError(f"Cannot capture integrated Qt UI for {scenario.code}")
    captured = tuple(args.destination.glob("UIX-*.png"))
    if len(captured) != 22:
        raise RuntimeError(f"Expected 22 integrated screen captures, got {len(captured)}")
    window.close()
    print("Captured 22 real embedded UIX22 screens in the single main-app shell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
