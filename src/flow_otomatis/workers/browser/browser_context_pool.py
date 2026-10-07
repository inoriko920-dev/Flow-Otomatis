"""Shared persistent Playwright context pool for one user-owned browser profile."""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright


class PlaywrightPersistentContextPool:
    """Own one persistent Chromium context per local profile id."""

    def __init__(self, browser_runtime_root: Path) -> None:
        self._browser_runtime_root = browser_runtime_root
        self._playwright: Playwright | None = None
        self._contexts: dict[str, BrowserContext] = {}

    def page(self, profile_id: str, user_data_dir: Path) -> Page:
        """Return one page from a profile-scoped persistent context."""

        context = self._contexts.get(profile_id)
        if context is None:
            context = self._launch_context(user_data_dir)
            self._contexts[profile_id] = context
        return context.pages[0] if context.pages else context.new_page()

    def close(self, profile_id: str) -> None:
        """Close one profile context while preserving its persisted browser data."""

        context = self._contexts.pop(profile_id, None)
        if context is not None:
            context.close()

    def shutdown(self) -> None:
        """Close every context and stop the Playwright runtime."""

        for profile_id in tuple(self._contexts):
            self.close(profile_id)
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def _launch_context(self, user_data_dir: Path) -> BrowserContext:
        user_data_dir.mkdir(parents=True, exist_ok=True)
        if self._browser_runtime_root.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(self._browser_runtime_root.resolve())
        playwright = self._playwright
        if playwright is None:
            playwright = sync_playwright().start()
            self._playwright = playwright
        return playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
        )
