"""Real Google Chrome manual login followed by Playwright CDP attachment.

Authentication is deliberately separated from automation:
1. Google sign-in happens in normal installed Chrome with no remote-debugging flag.
2. The user closes that login Chrome after authentication completes.
3. Only then is the same isolated profile relaunched with a localhost CDP endpoint.
4. Playwright attaches to the already-authenticated profile for read-only checks and Flow work.

No password, cookie, token, MFA value, or browser profile content crosses this boundary.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from collections.abc import Mapping
from contextlib import suppress
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


def build_manual_chrome_command(
    executable: Path,
    user_data_dir: Path,
    url: str,
) -> list[str]:
    """Build normal Chrome command for human Google authentication."""

    return [
        str(executable),
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-mode",
        url,
    ]


def build_debug_chrome_command(
    executable: Path,
    user_data_dir: Path,
    url: str = "about:blank",
) -> list[str]:
    """Build post-login Chrome command used only after manual authentication."""

    return [
        str(executable),
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-address=127.0.0.1",
        "--remote-debugging-port=0",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-mode",
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
    """Own normal-login Chrome and post-login CDP attachment per local profile."""

    def __init__(
        self,
        *,
        chrome_executable: Path | None = None,
        startup_timeout_s: float = _DEFAULT_STARTUP_TIMEOUT_S,
    ) -> None:
        self._chrome_executable = chrome_executable
        self._startup_timeout_s = startup_timeout_s
        self._manual_processes: dict[str, subprocess.Popen[bytes]] = {}
        self._debug_processes: dict[str, subprocess.Popen[bytes]] = {}
        self._browsers: dict[str, Browser] = {}
        self._pages: dict[str, Page] = {}
        self._playwright: Playwright | None = None

    def open_manual_page(self, profile_id: str, user_data_dir: Path, url: str) -> None:
        """Open Google sign-in in normal Chrome with no CDP/automation connection."""

        executable = self._chrome_executable or find_google_chrome_executable()
        user_data_dir.mkdir(parents=True, exist_ok=True)

        if profile_id in self._browsers or profile_id in self._debug_processes:
            self._close_debug_session(profile_id)

        process = self._manual_processes.get(profile_id)
        if process is not None and process.poll() is None:
            subprocess.Popen(
                build_manual_chrome_command(executable, user_data_dir, url),
                close_fds=True,
            )
            return

        process = subprocess.Popen(
            build_manual_chrome_command(executable, user_data_dir, url),
            close_fds=True,
        )
        self._manual_processes[profile_id] = process

    def page(self, profile_id: str, user_data_dir: Path) -> Page:
        """Attach after manual login and return one dedicated automation page."""

        page = self._pages.get(profile_id)
        if page is not None and not page.is_closed():
            return page

        manual_process = self._manual_processes.get(profile_id)
        if manual_process is not None and manual_process.poll() is None:
            raise FlowOtomatisError(
                "Login berjalan di Google Chrome normal. Setelah login selesai, "
                "tutup jendela Chrome tersebut lalu pilih Cek Ulang Sesi."
            )
        self._manual_processes.pop(profile_id, None)

        browser = self._browsers.get(profile_id)
        if browser is None or not browser.is_connected():
            browser = self._connect_after_login(profile_id, user_data_dir)
            self._browsers[profile_id] = browser

        if not browser.contexts:
            raise FlowOtomatisError(
                "Google Chrome tidak menyediakan context CDP yang dapat dipakai."
            )
        page = browser.contexts[0].new_page()
        self._pages[profile_id] = page
        return page

    def close(self, profile_id: str) -> None:
        """Close only Chrome processes created for one app-owned local profile."""

        self._close_debug_session(profile_id)
        process = self._manual_processes.pop(profile_id, None)
        if process is not None:
            self._terminate_process(process)

    def shutdown(self) -> None:
        """Close app-owned Chrome instances and release the Playwright CDP client."""

        profile_ids = (
            set(self._manual_processes)
            | set(self._debug_processes)
            | set(self._browsers)
            | set(self._pages)
        )
        for profile_id in tuple(profile_ids):
            self.close(profile_id)
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def _connect_after_login(self, profile_id: str, user_data_dir: Path) -> Browser:
        port = self._read_reachable_port(user_data_dir)
        if port is None:
            process = self._launch_debug_chrome(profile_id, user_data_dir)
            self._debug_processes[profile_id] = process
            self._wait_until_debug_ready(process, user_data_dir)
            port = read_devtools_active_port(user_data_dir)

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

    def _launch_debug_chrome(
        self,
        profile_id: str,
        user_data_dir: Path,
    ) -> subprocess.Popen[bytes]:
        del profile_id
        executable = self._chrome_executable or find_google_chrome_executable()
        active_port_file = user_data_dir / _DEVTOOLS_ACTIVE_PORT
        with suppress(OSError):
            active_port_file.unlink(missing_ok=True)
        return subprocess.Popen(
            build_debug_chrome_command(executable, user_data_dir),
            close_fds=True,
        )

    def _close_debug_session(self, profile_id: str) -> None:
        page = self._pages.pop(profile_id, None)
        if page is not None and not page.is_closed():
            with suppress(Exception):
                page.close()

        browser = self._browsers.pop(profile_id, None)
        if browser is not None and browser.is_connected():
            with suppress(Exception):
                browser.close()

        process = self._debug_processes.pop(profile_id, None)
        if process is not None:
            self._terminate_process(process)

    @staticmethod
    def _terminate_process(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

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
                raise FlowOtomatisError(
                    "Google Chrome mode Flow tertutup sebelum endpoint CDP siap. "
                    "Pastikan semua jendela Chrome login sudah ditutup lalu coba lagi."
                )
            if self._read_reachable_port(user_data_dir) is not None:
                return
            time.sleep(0.1)
        self._terminate_process(process)
        raise FlowOtomatisError(
            "Profil Chrome masih dipakai oleh proses lain atau CDP belum siap. "
            "Tutup jendela Chrome login lalu pilih Cek Ulang Sesi lagi."
        )
