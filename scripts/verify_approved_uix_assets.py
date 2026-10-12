"""Fail CI if any of the 22 frozen owner-approved UI PNG digests differ."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_otomatis.presentation.approved_uix_assets import (
    APPROVED_IMAGES,
    load_verified_reference,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("assets_folder", type=Path)
    args = parser.parse_args()
    if len(APPROVED_IMAGES) != 22:
        raise RuntimeError("Expected exactly 22 owner-approved assets")
    for code in sorted(APPROVED_IMAGES):
        validated = load_verified_reference(code, supplied_directory=args.assets_folder)
        print(f"VERIFIED {code}: {validated.name}")
    print("22/22 immutable UI PNG SHA-256 digests match approved manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
