"""Launch staged Chromium against a deterministic local page."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def smoke(browser_root: Path) -> None:
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_root.resolve())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content("<title>Flow-Otomatis Foundation</title><h1>ready</h1>")
            if page.title() != "Flow-Otomatis Foundation":
                raise RuntimeError("Chromium smoke page title mismatch")
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "browser_root",
        nargs="?",
        type=Path,
        default=Path(".runtime/browsers"),
    )
    args = parser.parse_args()
    smoke(args.browser_root)
    print("Playwright Chromium smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
