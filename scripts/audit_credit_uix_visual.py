"""Read-only visual QA pairing of approved mockups with real Qt screenshots.

Does NOT replace reference images or declare pixel parity. The reference branch
is fetched only into a separate worktree in the Windows CI job. The resulting
report identifies screens requiring a human pixel/layout review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication

from flow_otomatis.presentation.credit_uix_preview import UIX_SCENARIOS


def _average_difference(reference: QImage, actual: QImage) -> float:
    """Sample a coarse thumbnail for triage, not a design acceptance score."""
    ref = reference.scaled(120, 68, Qt.AspectRatioMode.IgnoreAspectRatio)
    new = actual.scaled(120, 68, Qt.AspectRatioMode.IgnoreAspectRatio)
    total = 0
    for y in range(68):
        for x in range(120):
            a = ref.pixelColor(x, y)
            b = new.pixelColor(x, y)
            total += abs(a.red() - b.red())
            total += abs(a.green() - b.green())
            total += abs(a.blue() - b.blue())
    return round(total / (120 * 68 * 3), 2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("approved_assets", type=Path)
    parser.add_argument("rendered_captures", type=Path)
    parser.add_argument("review_output", type=Path)
    args = parser.parse_args()
    # QPainter.drawText requires a Qt GUI application for font metrics on Windows.
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    args.review_output.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    for state in UIX_SCENARIOS:
        suffix = state.code.replace("-", "_")
        matches = sorted(args.approved_assets.glob(f"*{suffix}_*.png"))
        if len(matches) != 1:
            raise RuntimeError(
                f"{state.code}: expected exactly one frozen reference, got {len(matches)}"
            )
        capture = args.rendered_captures / f"{state.code}.png"
        if not capture.is_file():
            raise RuntimeError(f"{state.code}: real Qt capture absent")
        approved = QImage(str(matches[0]))
        rendered = QImage(str(capture))
        if approved.isNull() or rendered.isNull():
            raise RuntimeError(f"{state.code}: unable to load visual reference or render")
        if (approved.width(), approved.height()) != (1920, 1080):
            raise RuntimeError(f"{state.code}: approved image must stay 1920x1080")
        if (rendered.width(), rendered.height()) != (1920, 1080):
            raise RuntimeError(f"{state.code}: latest Qt render must be 1920x1080")

        pair = QImage(1920, 588, QImage.Format.Format_RGB32)
        pair.fill(QColor("white"))
        painter = QPainter(pair)
        painter.setPen(QColor("#111827"))
        painter.drawText(
            0,
            0,
            960,
            38,
            int(Qt.AlignmentFlag.AlignCenter),
            f"{state.code} • REFERENSI OWNER-APPROVED",
        )
        painter.drawText(
            960,
            0,
            960,
            38,
            int(Qt.AlignmentFlag.AlignCenter),
            f"{state.code} • RENDER Qt (REVIEW)",
        )
        painter.drawImage(0, 42, approved.scaled(960, 540))
        painter.drawImage(960, 42, rendered.scaled(960, 540))
        painter.end()
        output = args.review_output / f"{state.code}_SIDE_BY_SIDE.png"
        if not pair.save(str(output)):
            raise RuntimeError(f"{state.code}: failed to save side-by-side review")
        results.append(
            {
                "state": state.code,
                "reference": matches[0].name,
                "render": capture.name,
                "comparison": output.name,
                "resolution": [1920, 1080],
                "mean_rgb_difference_sample": _average_difference(approved, rendered),
                "decision": "HUMAN_VISUAL_REVIEW_REQUIRED",
            }
        )
    if len(results) != 22:
        raise RuntimeError("The 22 approved UI states are incomplete")

    manifest = {
        "count": len(results),
        "state": "VISUAL_COMPARISON_AVAILABLE_NOT_PIXEL_PARITY",
        "warning": (
            "Measured color difference is for identifying layouts to inspect, "
            "NOT a PASS threshold or proof of fidelity."
        ),
        "items_by_highest_difference": sorted(
            results, key=lambda item: float(item["mean_rgb_difference_sample"]), reverse=True
        ),
    }
    (args.review_output / "UIX22_REVIEW_REPORT.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Prepared 22 side-by-side comparisons; pixel parity remains UNVERIFIED")
    print("Highest sampled RGB differences (priorities for manual layout review):")
    for item in manifest["items_by_highest_difference"][:8]:
        print(f"  {item['state']}: {item['mean_rgb_difference_sample']} / 255")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
