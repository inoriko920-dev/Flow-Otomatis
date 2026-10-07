"""Capture ACTUAL screenshots for all frozen STEP 04 UI fixture states."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from flow_otomatis.presentation.fixtures import FIXTURE_CODES
from flow_otomatis.presentation.main_window import MainWindow


def capture(output_dir: Path) -> list[Path]:
    """Render every frozen fixture at the reference 1920x1080 viewport."""

    output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = MainWindow()
    window.setFixedSize(1920, 1080)
    window.show()
    written: list[Path] = []

    for code in FIXTURE_CODES:
        window.show_fixture(code)
        app.processEvents()
        QTest.qWait(40)
        image = window.grab()
        if image.width() != 1920 or image.height() != 1080:
            raise RuntimeError(f"{code}: expected 1920x1080, got {image.width()}x{image.height()}")
        path = output_dir / f"{code}.png"
        if not image.save(str(path), "PNG"):
            raise RuntimeError(f"Could not save screenshot: {path}")
        written.append(path)

    window.close()
    app.processEvents()
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        default=Path("artifacts/ui_actual"),
    )
    args = parser.parse_args()
    paths = capture(args.output_dir.resolve())
    print(f"Captured {len(paths)} ACTUAL UI screenshots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
