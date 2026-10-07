"""Playwright-owned authorized Google session lifecycle.

This module deliberately exposes only credential-free status metadata. Persistent
browser data stays below the user-scoped Sessions root and is never copied into
projects, logs, diagnostics, or handoff manifests.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse
from uuid import uuid4

from playwright.sync_api import (
    BrowserContext,
    Error as PlaywrightError,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from flow_otomatis.application.ports.google_session import (
    GoogleSessionPort,
    GoogleSessionProfile,
    GoogleSessionState,
)
from flow_otomatis.domain.errors import FlowOtomatisError

_PROFILE_ID = re.compile(r"^profile-[0-9a-f]{12}$")
_METADATA_NAME = "profile.json"
_GOOGLE_LOGIN_URL = "https://accounts.google.com/"
_GOOGLE_ACCOUNT_URL = "https://myaccount.google.com/"


@dataclass(frozen=True, slots=True)
class BrowserSessionProbe:
    """Sanitized browser result with no URL query, cookie, token, or credential data."""

    state: GoogleSessionState
    detail: str


class GoogleSessionBrowserDriver(Protocol):
    """Tiny seam that makes browser behavior fixture-testable."""

    def open_login(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        """Open/focus the official Google login page."""

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        """Probe authorization using navigation only."""

    def close(self, profile_id: str) -> None:
        """Close one persistent browser context."""

    def shutdown(self) -> None:
        """Close all owned browser resources."""


class PlaywrightGoogleSessionDriver:
    """Real Playwright implementation; no generation mutation is performed here."""

    def __init__(self, browser_runtime_root: Path) -> None:
        self._browser_runtime_root = browser_runtime_root
        self._playwright: Playwright | None = None
        self._contexts: dict[str, BrowserContext] = {}

    def open_login(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        page = self._page(profile_id, user_data_dir)
        try:
            page.goto(_GOOGLE_LOGIN_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            page.bring_to_front()
        except PlaywrightTimeoutError:
            return BrowserSessionProbe(
                GoogleSessionState.UNKNOWN,
                "Halaman login resmi belum selesai dimuat sebelum timeout.",
            )
        except PlaywrightError:
            return BrowserSessionProbe(
                GoogleSessionState.ERROR,
                "Browser tidak dapat membuka halaman login resmi.",
            )
        return BrowserSessionProbe(
            GoogleSessionState.NEEDS_LOGIN,
            "Selesaikan login, MFA, atau CAPTCHA secara manual pada halaman resmi Google.",
        )

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        page = self._page(profile_id, user_data_dir)
        try:
            page.goto(_GOOGLE_ACCOUNT_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            page.bring_to_front()
        except PlaywrightTimeoutError:
            return BrowserSessionProbe(
                GoogleSessionState.UNKNOWN,
                "Pemeriksaan sesi melewati batas waktu; tidak ada submit yang dilakukan.",
            )
        except PlaywrightError:
            return BrowserSessionProbe(
                GoogleSessionState.ERROR,
                "Browser gagal memeriksa sesi; data kredensial tidak dibaca.",
            )

        hostname = (urlparse(page.url).hostname or "").lower()
        if hostname == "myaccount.google.com":
            return BrowserSessionProbe(
                GoogleSessionState.READY,
                "Sesi Google terotorisasi dan siap digunakan.",
            )
        if hostname == "accounts.google.com":
            return BrowserSessionProbe(
                GoogleSessionState.NEEDS_LOGIN,
                "Login manual diperlukan pada halaman resmi Google.",
            )
        return BrowserSessionProbe(
            GoogleSessionState.UNKNOWN,
            "Status sesi belum dapat dipastikan; periksa kembali tanpa submit ulang.",
        )

    def close(self, profile_id: str) -> None:
        context = self._contexts.pop(profile_id, None)
        if context is not None:
            context.close()

    def shutdown(self) -> None:
        for profile_id in tuple(self._contexts):
            self.close(profile_id)
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def _page(self, profile_id: str, user_data_dir: Path) -> Page:
        context = self._contexts.get(profile_id)
        if context is None:
            context = self._launch_context(user_data_dir)
            self._contexts[profile_id] = context
        return context.pages[0] if context.pages else context.new_page()

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


class GoogleSessionWorker(GoogleSessionPort):
    """Persist safe metadata and delegate browser actions to the Browser Worker."""

    def __init__(
        self,
        session_root: Path,
        browser_runtime_root: Path,
        *,
        driver: GoogleSessionBrowserDriver | None = None,
        timeout_ms: int = 20_000,
    ) -> None:
        self._root = session_root / "google"
        self._driver = driver or PlaywrightGoogleSessionDriver(browser_runtime_root)
        self._timeout_ms = timeout_ms

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        if not self._root.exists():
            return ()
        profiles: list[GoogleSessionProfile] = []
        for profile_root in sorted(self._root.iterdir(), key=lambda path: path.name):
            if not profile_root.is_dir() or not _PROFILE_ID.fullmatch(profile_root.name):
                continue
            try:
                profiles.append(self._read_profile(profile_root.name))
            except FlowOtomatisError:
                profiles.append(
                    GoogleSessionProfile(
                        profile_id=profile_root.name,
                        label=profile_root.name,
                        state=GoogleSessionState.ERROR,
                        last_checked_at=None,
                        detail="Metadata sesi lokal tidak dapat dibaca.",
                    )
                )
        return tuple(profiles)

    def create_profile(self, label: str) -> GoogleSessionProfile:
        self._root.mkdir(parents=True, exist_ok=True)
        while True:
            profile_id = f"profile-{uuid4().hex[:12]}"
            profile_root = self._root / profile_id
            try:
                profile_root.mkdir(parents=False, exist_ok=False)
                break
            except FileExistsError:
                continue

        profile = GoogleSessionProfile(
            profile_id=profile_id,
            label=label,
            state=GoogleSessionState.NEEDS_LOGIN,
            last_checked_at=None,
            detail="Profil dibuat. Login manual diperlukan.",
        )
        self._write_profile(profile)
        return profile

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        profile = self._read_profile(profile_id)
        probe = self._driver.open_login(
            profile_id,
            self._browser_data_dir(profile_id),
            timeout_ms=self._timeout_ms,
        )
        updated = GoogleSessionProfile(
            profile_id=profile.profile_id,
            label=profile.label,
            state=probe.state,
            last_checked_at=profile.last_checked_at,
            detail=probe.detail,
        )
        self._write_profile(updated)
        return updated

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        profile = self._read_profile(profile_id)
        probe = self._driver.check(
            profile_id,
            self._browser_data_dir(profile_id),
            timeout_ms=self._timeout_ms,
        )
        updated = GoogleSessionProfile(
            profile_id=profile.profile_id,
            label=profile.label,
            state=probe.state,
            last_checked_at=datetime.now(UTC),
            detail=probe.detail,
        )
        self._write_profile(updated)
        return updated

    def cancel_profile(self, profile_id: str) -> None:
        self._validated_profile_root(profile_id)
        self._driver.close(profile_id)

    def delete_profile(self, profile_id: str) -> None:
        profile_root = self._validated_profile_root(profile_id)
        if not profile_root.exists():
            raise FlowOtomatisError("Profil Google lokal tidak ditemukan.")
        self._driver.close(profile_id)
        shutil.rmtree(profile_root)

    def shutdown(self) -> None:
        self._driver.shutdown()

    def _browser_data_dir(self, profile_id: str) -> Path:
        return self._validated_profile_root(profile_id) / "browser-data"

    def _validated_profile_root(self, profile_id: str) -> Path:
        if not _PROFILE_ID.fullmatch(profile_id):
            raise FlowOtomatisError("ID profil Google tidak valid.")
        return self._root / profile_id

    def _read_profile(self, profile_id: str) -> GoogleSessionProfile:
        profile_root = self._validated_profile_root(profile_id)
        metadata_path = profile_root / _METADATA_NAME
        if not metadata_path.is_file():
            raise FlowOtomatisError("Metadata profil Google lokal tidak ditemukan.")
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            label = str(payload["label"])
            state = GoogleSessionState(str(payload["state"]))
            checked_raw = payload.get("last_checked_at")
            checked = datetime.fromisoformat(str(checked_raw)) if checked_raw else None
            detail = str(payload["detail"])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise FlowOtomatisError("Metadata profil Google lokal tidak valid.") from exc
        return GoogleSessionProfile(
            profile_id=profile_id,
            label=label,
            state=state,
            last_checked_at=checked,
            detail=detail,
        )

    def _write_profile(self, profile: GoogleSessionProfile) -> None:
        profile_root = self._validated_profile_root(profile.profile_id)
        profile_root.mkdir(parents=True, exist_ok=True)
        payload = {
            "profile_id": profile.profile_id,
            "label": profile.label,
            "state": profile.state.value,
            "last_checked_at": (
                profile.last_checked_at.isoformat() if profile.last_checked_at is not None else None
            ),
            "detail": profile.detail,
        }
        metadata_path = profile_root / _METADATA_NAME
        temp_path = metadata_path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(metadata_path)
