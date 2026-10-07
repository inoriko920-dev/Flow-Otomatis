"""Compare ACTUAL UI screenshots against the frozen STEP 04 reference DOCX."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from flow_otomatis.presentation.fixtures import FIXTURE_CODES

_MEDIA_PATTERN = re.compile(r"image(\d+)\.(?:jpg|jpeg|png)$", re.IGNORECASE)
_COMPARE_WIDTH = 96
_COMPARE_HEIGHT = 54


def _media_sort_key(name: str) -> int:
    match = _MEDIA_PATTERN.search(name)
    if match is None:
        return 10_000
    return int(match.group(1))


def extract_references(docx_path: Path, output_dir: Path) -> list[Path]:
    """Extract the 30 embedded final references in fixture order."""

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path) as archive:
        media = sorted(
            (
                name
                for name in archive.namelist()
                if name.startswith("word/media/") and _MEDIA_PATTERN.search(name)
            ),
            key=_media_sort_key,
        )
        if len(media) != len(FIXTURE_CODES):
            raise RuntimeError(
                f"Expected {len(FIXTURE_CODES)} reference images, found {len(media)}"
            )

        paths: list[Path] = []
        for code, media_name in zip(FIXTURE_CODES, media, strict=True):
            image = QImage.fromData(archive.read(media_name))
            if image.isNull():
                raise RuntimeError(f"Could not decode reference image: {media_name}")
            path = output_dir / f"{code}.png"
            if not image.save(str(path), "PNG"):
                raise RuntimeError(f"Could not save extracted reference: {path}")
            paths.append(path)
        return paths


def _scaled(path: Path) -> QImage:
    image = QImage(str(path))
    if image.isNull():
        raise RuntimeError(f"Could not read image: {path}")
    return image.scaled(
        _COMPARE_WIDTH,
        _COMPARE_HEIGHT,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    ).convertToFormat(QImage.Format.Format_RGB32)


def visual_similarity(reference: Path, actual: Path) -> float:
    """Return low-frequency RGB similarity in the range 0..1."""

    ref = _scaled(reference)
    act = _scaled(actual)
    difference = 0
    samples = _COMPARE_WIDTH * _COMPARE_HEIGHT * 3
    for y in range(_COMPARE_HEIGHT):
        for x in range(_COMPARE_WIDTH):
            ref_color = ref.pixelColor(x, y)
            act_color = act.pixelColor(x, y)
            difference += abs(ref_color.red() - act_color.red())
            difference += abs(ref_color.green() - act_color.green())
            difference += abs(ref_color.blue() - act_color.blue())
    return 1.0 - (difference / (samples * 255.0))


def compare(
    reference_dir: Path,
    actual_dir: Path,
    report_path: Path,
    *,
    minimum_similarity: float,
) -> list[tuple[str, float, bool]]:
    """Compare the full frozen reference set and write a Markdown report."""

    results: list[tuple[str, float, bool]] = []
    for code in FIXTURE_CODES:
        reference = reference_dir / f"{code}.png"
        actual = actual_dir / f"{code}.png"
        if not actual.is_file():
            raise RuntimeError(f"Missing ACTUAL screenshot: {actual}")
        score = visual_similarity(reference, actual)
        results.append((code, score, score >= minimum_similarity))

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# STEP 09 UI Visual Comparison",
        "",
        f"Low-frequency RGB similarity gate: **{minimum_similarity:.3f}**",
        "",
        "| Fixture | Similarity | Status |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| {code} | {score:.4f} | {'PASS' if passed else 'FAIL'} |"
        for code, score, passed in results
    )
    lines.extend(
        [
            "",
            "> This pixel-frequency gate is supplemental. Semantic UI contract tests remain "
            "authoritative for copy, status, navigation, safety, and frozen workflow meaning.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference-docx",
        type=Path,
        default=Path(
            "docs/ui/04_STEP_04_FINAL_UI_REFERENCE_"
            "FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx"
        ),
    )
    parser.add_argument(
        "--actual-dir",
        type=Path,
        default=Path("artifacts/ui_actual"),
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=Path("artifacts/ui_reference"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("artifacts/ui_visual_report.md"),
    )
    parser.add_argument("--minimum-similarity", type=float, default=0.55)
    args = parser.parse_args()

    extract_references(args.reference_docx, args.reference_dir)
    results = compare(
        args.reference_dir,
        args.actual_dir,
        args.report,
        minimum_similarity=args.minimum_similarity,
    )

    failures = [code for code, _score, passed in results if not passed]
    print(
        "Visual similarity range: "
        f"{min(score for _code, score, _passed in results):.4f}.."
        f"{max(score for _code, score, _passed in results):.4f}"
    )
    if failures:
        print("Visual comparison failed: " + ", ".join(failures))
        return 1
    print(f"Visual comparison passed for {len(results)} fixtures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
