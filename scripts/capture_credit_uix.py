"""Capture real Qt renders of all 22 UIX preview states in offline mode."""

from __future__ import annotations

import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication

from flow_otomatis.presentation.credit_uix_preview import UIX_SCENARIOS, CreditUixDialog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    dialog = CreditUixDialog()
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
