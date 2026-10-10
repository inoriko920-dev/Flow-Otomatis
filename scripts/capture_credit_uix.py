"""Capture real Qt renders of all 22 UIX preview states in offline mode."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
from PySide6.QtWidgets import QApplication

from flow_otomatis.presentation.credit_uix_preview import UIX_SCENARIOS, CreditUixDialog


def _ensure_readable_capture_font() -> None:
    """Fail visual QA if Qt offscreen renders tofu boxes rather than text."""

    if os.name == "nt":
        # This is the runner's installed Windows system font; do not bundle or
        # publish font files. Offscreen Qt may not discover Windows fonts itself.
        system_font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/segoeui.ttf"
        if not system_font.is_file():
            raise RuntimeError("Windows Segoe UI font unavailable for trustworthy UI capture")
        font_id = QFontDatabase.addApplicationFont(str(system_font))
        if font_id < 0:
            raise RuntimeError("Qt failed to load local Segoe UI font for visual QA")
        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            raise RuntimeError("Qt registered no usable family from Windows Segoe UI")
        resolved_font = QFont(families[0], 9)
    else:
        resolved_font = QFont("DejaVu Sans", 9)

    metrics = QFontMetrics(resolved_font)
    if metrics.horizontalAdvance("IIIIIIII") >= metrics.horizontalAdvance("WWWWWWWW"):
        raise RuntimeError("Qt rendered monospaced tofu-like glyphs; UI visual QA is INVALID")
    QApplication.setFont(resolved_font)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _ensure_readable_capture_font()
    dialog = CreditUixDialog()
    # The approved UI references are 1920x1080 screenshots; keep render canvas exact.
    dialog.resize(1920, 1080)
    dialog.show()
    for scenario in UIX_SCENARIOS:
        dialog.set_state(scenario.code)
        app.processEvents()
        output = args.destination / f"{scenario.code}.png"
        if not dialog.grab().save(str(output)):
            raise RuntimeError(f"Failed to capture {scenario.code}")
    dialog.close()
    captures = sorted(args.destination.glob("UIX-*.png"))
    if len(captures) != 22:
        raise RuntimeError(f"Expected 22 Qt screenshots, got {len(captures)}")
    print(f"Captured {len(captures)} real Qt UI states; all labeled simulation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
