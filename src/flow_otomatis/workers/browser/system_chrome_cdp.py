"""System Google Chrome launcher plus Playwright CDP attachment.

Manual Google authentication happens in a real installed Chrome process before
Playwright attaches. The app uses an isolated non-default user-data directory,
a random localhost debugging port, and never exports browser credentials.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from flow_otomatis.domain.errors import FlowOtomatisError

_DEVTOOLS_ACTIVE_PORT = "DevToolsActivePort"
_DEFAULT_STARTUP_TIMEOUT_S = 15.0


def find_google_chrome_executable(
    *,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Find an installed Google Chrome without launching or modifying it."""

    env = environ if environ is not None else os.environ
    candidates: list[Path] = []
    for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        root = env.get(key)
        if root:
            candidates.append(Path(root) / "Google" / "Chrome" / "Application" / "chrome.exe")

    which = shutil.which("chrome.exe") or shutil.which("chrome")
    if which:
        candidates.append(Path(which))

    if os.name == "nt":
        candidates.extend(_registry_chrome_candidates())

    seen: set[str] = set()
    for candidate in candidates:
        normalized = str(candidate).casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        if candidate.is_file():
            return candidate.resolve()

    raise FlowOtomatisError(
        "Google Chrome tidak ditemukan. Instal Google Chrome resmi lalu buka kembali Flow-Otomatis."
    )


def build_system_chrome_command(
    executable: Path,
    user_data_dir: Path,
    url: str,
) -> list[str]:
    """Build the minimal real-Chrome launch command used for manual login."""

    return [
        str(executable),
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-address=127.0.0.1",
        "--remote-debugging-port=0",
        "--no-first-run",
        "--no-default-browser-check",
        url,
    ]


def read_devtools_active_port(user_data_dir: Path) -> int:
    """Read Chrome's random localhost CDP port from its dedicated profile."""

    path = user_data_dir / _DEVTOOLS_ACTIVE_PORT
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0].strip()
        port = int(first_line)
    except (OSError, IndexError, ValueError) as exc:
        raise FlowOtomatisError("Endpoint debug lokal Google Chrome belum siap.") from exc
    if not 1 <= port <= 65535:
        raise FlowOtomatisError("Port debug lokal Google Chrome tidak valid.")
    return port


def _registry_chrome_candidates() -> tuple[Path, ...]:
    try:
        import winreg
    except ImportError:
        return ()

    paths: list[Path] = []
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                value, _kind = winreg.QueryValueEx(key, None)
        except OSError:
            continue
        if value:
            paths.append(Path(str(value)))
    return tuple(paths)


def _port_is_reachable(port: int, *, timeout_s: float = 0.25) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout_s):
            return True
    except OSError:
        return False


class SystemChromeCdpPool:
    """Own one real Google Chrome process and one CDP attachment per local profile."""

    def __init__(
        self,
        *,
        chrome_executable: Path | None = None,
        startup_timeout_s: float = _DEFAULT_STARTUP_TIMEOUT_S,
    ) -> None:
        self._chrome_executable = chrome_executable
        self._startup_timeout_s = startup_timeout_s
        self._processes: dict[str, subprocess.Popen[bytes]] = {}
        self._browsers: dict[str, Browser] = {}
        self._pages: dict[str, Page] = {}
        self._playwright: Playwright | None = None

    def open_manual_page(self, profile_id: str, user_data_dir: Path, url: str) -> None:
        """Open a real Chrome login page without attaching Playwright."""

        executable = self._chrome_executable or find_google_chrome_executable()
        user_data_dir.mkdir(parents=True, exist_ok=True)

        existing_port = self._read_reachable_port(user_data_dir)
        if existing_port is not None:
            subprocess.Popen(
                [str(executable), f"--user-data-dir={user_data_dir}", url],
                close_fds=True,
            )
            return

        active_port_file = user_data_dir / _DEVTOOLS_ACTIVE_PORT
        try:
            active_port_file.unlink(missing_ok=True)
        except OSError as exc:
            raise FlowOtomatisError(
                "Profil Chrome lokal sedang terkunci dan tidak dapat disiapkan."
            ) from exc

        process = subprocess.Popen(
            build_system_chrome_command(executable, user_data_dir, url),
            close_fds=True,
        )
        self._processes[profile_id] = process
        self._wait_until_debug_ready(process, user_data_dir)

    def page(self, profile_id: str, user_data_dir: Path) -> Page:
        """Return a dedicated automation page after manual authentication."""

        page = self._pages.get(profile_id)
        if page is not None and not page.is_closed():
            return page

        browser = self._browsers.get(profile_id)
        if browser is None or not browser.is_connected():
            browser = self._connect(profile_id, user_data_dir)
            self._browsers[profile_id] = browser

        if not browser.contexts:
            raise FlowOtomatisError(
                "Google Chrome tidak menyediakan context CDP yang dapat dipakai."
            )
        page = browser.contexts[0].new_page()
        self._pages[profile_id] = page
        return page

    def close(self, profile_id: str) -> None:
        """Close only the app-owned dedicated Chrome profile process."""

        page = self._pages.pop(profile_id, None)
        if page is not None and not page.is_closed():
            try:
                page.close()
            except Exception:
                pass

        browser = self._browsers.pop(profile_id, None)
        if browser is not None and browser.is_connected():
            try:
                browser.close()
            except Exception:
                pass

        process = self._processes.pop(profile_id, None)
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    def shutdown(self) -> None:
        """Close app-owned Chrome instances and release the Playwright CDP client."""

        profile_ids = set(self._processes) | set(self._browsers) | set(self._pages)
        for profile_id in tuple(profile_ids):
            self.close(profile_id)
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def _connect(self, profile_id: str, user_data_dir: Path) -> Browser:
        del profile_id
        port = self._read_reachable_port(user_data_dir)
        if port is None:
            raise FlowOtomatisError(
                "Google Chrome profil ini tidak sedang berjalan. Pilih Buka / Fokuskan Sesi Login."
            )
        playwright = self._playwright
        if playwright is None:
            playwright = sync_playwright().start()
            self._playwright = playwright
        try:
            return playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as exc:
            raise FlowOtomatisError(
                "Flow-Otomatis gagal terhubung ke Google Chrome melalui CDP lokal."
            ) from exc

    def _read_reachable_port(self, user_data_dir: Path) -> int | None:
        try:
            port = read_devtools_active_port(user_data_dir)
        except FlowOtomatisError:
            return None
        return port if _port_is_reachable(port) else None

    def _wait_until_debug_ready(
        self,
        process: subprocess.Popen[bytes],
        user_data_dir: Path,
    ) -> None:
        deadline = time.monotonic() + self._startup_timeout_s
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise FlowOtomatisError("Google Chrome tertutup sebelum profil login siap.")
            if self._read_reachable_port(user_data_dir) is not None:
                return
            time.sleep(0.1)
        raise FlowOtomatisError(
            "Google Chrome terbuka, tetapi endpoint CDP lokal belum siap. Coba buka sesi lagi."
        )
