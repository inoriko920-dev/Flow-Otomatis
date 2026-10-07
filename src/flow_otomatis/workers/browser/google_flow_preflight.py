"""Read-only Google Flow access preflight.

This module intentionally does not inspect generation controls, upload assets,
type prompts, or click any mutating control. It only navigates to Google's
official Flow surface and classifies sanitized reachability/auth evidence.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowAccessState,
    GoogleFlowPreflightPort,
)
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.workers.browser.system_chrome_cdp import SystemChromeCdpPool

_PROFILE_ID = re.compile(r"^profile-[0-9a-f]{12}$")
_GOOGLE_FLOW_URL = "https://labs.google/fx/tools/flow"


class GoogleFlowPreflightDriver(Protocol):
    """Tiny read-only browser seam for fixture tests."""

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> tuple[GoogleFlowAccessState, str]:
        """Open Flow without mutating user content."""

    def close(self, profile_id: str) -> None:
        """Close one browser context."""

    def shutdown(self) -> None:
        """Release browser resources."""


class PlaywrightGoogleFlowPreflightDriver:
    """Read-only Playwright preflight using a shared persistent context pool."""

    def __init__(self, context_pool: SystemChromeCdpPool) -> None:
        self._context_pool = context_pool

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> tuple[GoogleFlowAccessState, str]:
        page = self._context_pool.page(profile_id, user_data_dir)
        try:
            response = page.goto(
                _GOOGLE_FLOW_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )
            page.bring_to_front()
        except PlaywrightTimeoutError:
            return (
                GoogleFlowAccessState.UNKNOWN,
                "Flow belum selesai dimuat sebelum timeout; tidak ada aksi pembuatan dilakukan.",
            )
        except PlaywrightError:
            return (
                GoogleFlowAccessState.ERROR,
                "Browser gagal membuka Flow; tidak ada aksi pembuatan dilakukan.",
            )

        if response is not None and response.status >= 400:
            return (
                GoogleFlowAccessState.UNAVAILABLE,
                f"Flow mengembalikan HTTP {response.status}; tidak ada aksi pembuatan dilakukan.",
            )

        hostname = (urlparse(page.url).hostname or "").lower()
        if hostname == "accounts.google.com":
            return (
                GoogleFlowAccessState.AUTH_REQUIRED,
                "Flow mengarahkan ke login Google; selesaikan login secara manual.",
            )
        if hostname == "labs.google" or hostname.endswith(".labs.google"):
            return (
                GoogleFlowAccessState.REACHABLE,
                "Halaman resmi Google Flow dapat dijangkau. Generate belum diuji.",
            )
        return (
            GoogleFlowAccessState.UNKNOWN,
            "Flow terbuka pada host yang tidak dikenali; tidak ada aksi pembuatan dilakukan.",
        )

    def close(self, profile_id: str) -> None:
        self._context_pool.close(profile_id)

    def shutdown(self) -> None:
        self._context_pool.shutdown()


class GoogleFlowPreflightWorker(GoogleFlowPreflightPort):
    """Validate a local profile and perform one read-only Flow preflight."""

    def __init__(
        self,
        session_root: Path,
        browser_runtime_root: Path | None = None,
        *,
        context_pool: SystemChromeCdpPool | None = None,
        driver: GoogleFlowPreflightDriver | None = None,
        timeout_ms: int = 20_000,
    ) -> None:
        self._root = session_root / "google"
        del browser_runtime_root
        pool = context_pool or SystemChromeCdpPool()
        self._driver = driver or PlaywrightGoogleFlowPreflightDriver(pool)
        self._timeout_ms = timeout_ms

    def check(self, profile_id: str) -> GoogleFlowAccessProbe:
        user_data_dir = self._browser_data_dir(profile_id)
        state, detail = self._driver.check(
            profile_id,
            user_data_dir,
            timeout_ms=self._timeout_ms,
        )
        return GoogleFlowAccessProbe(
            profile_id=profile_id,
            state=state,
            checked_at=datetime.now(UTC),
            detail=detail[:500],
        )

    def close(self, profile_id: str) -> None:
        self._validated_profile_root(profile_id)
        self._driver.close(profile_id)

    def shutdown(self) -> None:
        self._driver.shutdown()

    def _browser_data_dir(self, profile_id: str) -> Path:
        profile_root = self._validated_profile_root(profile_id)
        metadata_path = profile_root / "profile.json"
        if not metadata_path.is_file():
            raise FlowOtomatisError("Profil Google lokal belum tersedia untuk Flow preflight.")
        return profile_root / "browser-data"

    def _validated_profile_root(self, profile_id: str) -> Path:
        if not _PROFILE_ID.fullmatch(profile_id):
            raise FlowOtomatisError("ID profil Google tidak valid.")
        return self._root / profile_id
