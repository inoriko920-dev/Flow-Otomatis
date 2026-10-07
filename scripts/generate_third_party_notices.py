"""Generate a simple dependency provenance notice for the portable artifact."""

from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path

PACKAGES = (
    "PySide6",
    "shiboken6",
    "playwright",
    "pydantic",
    "keyring",
    "PyInstaller",
)


def generate(destination: Path) -> None:
    lines = [
        "Flow-Otomatis — Third-Party Dependency Notice",
        "",
        "This inventory records package versions and package-provided license metadata.",
        "Review upstream license texts before a public production release.",
        "",
    ]
    for package in PACKAGES:
        info = metadata.metadata(package)
        version = metadata.version(package)
        license_value = info.get("License-Expression") or info.get("License") or "See upstream metadata"
        project_url = info.get("Home-page") or next(
            (value.split(",", 1)[-1].strip() for value in info.get_all("Project-URL", []) if "," in value),
            "See PyPI metadata",
        )
        lines.extend(
            [
                f"{package} {version}",
                f"  License: {license_value}",
                f"  Project: {project_url}",
                "",
            ]
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=Path("dist/THIRD_PARTY_NOTICES.txt"),
    )
    args = parser.parse_args()
    generate(args.destination)
    print(f"Wrote {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
