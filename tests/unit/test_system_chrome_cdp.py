from __future__ import annotations

from pathlib import Path

import pytest

from flow_otomatis.application.ports.google_session import GoogleSessionState
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.workers.browser.google_session_worker import (
    SystemChromeGoogleSessionDriver,
)
from flow_otomatis.workers.browser.system_chrome_cdp import (
    build_debug_chrome_command,
    build_manual_chrome_command,
    find_google_chrome_executable,
    read_devtools_active_port,
)


class FixtureChromePool:
    def __init__(self) -> None:
        self.manual_calls: list[tuple[str, Path, str]] = []
        self.page_calls = 0

    def open_manual_page(self, profile_id: str, user_data_dir: Path, url: str) -> None:
        self.manual_calls.append((profile_id, user_data_dir, url))

    def page(self, profile_id: str, user_data_dir: Path):
        del profile_id, user_data_dir
        self.page_calls += 1
        raise AssertionError("Playwright/CDP must not attach during manual login")

    def close(self, profile_id: str) -> None:
        del profile_id

    def shutdown(self) -> None:
        pass


def test_manual_chrome_command_has_no_remote_debugging_or_automation_flags(tmp_path: Path) -> None:
    chrome = tmp_path / "chrome.exe"
    profile = tmp_path / "profile"
    command = build_manual_chrome_command(chrome, profile, "https://accounts.google.com/")

    assert command[0] == str(chrome)
    assert f"--user-data-dir={profile}" in command
    serialized = " ".join(command).casefold()
    assert "remote-debugging" not in serialized
    assert "--enable-automation" not in serialized
    assert "automationcontrolled" not in serialized
    assert "undetected" not in serialized


def test_post_login_debug_command_uses_random_localhost_cdp_without_stealth(
    tmp_path: Path,
) -> None:
    chrome = tmp_path / "chrome.exe"
    profile = tmp_path / "profile"
    command = build_debug_chrome_command(chrome, profile)

    assert f"--user-data-dir={profile}" in command
    assert "--remote-debugging-address=127.0.0.1" in command
    assert "--remote-debugging-port=0" in command
    serialized = " ".join(command).casefold()
    assert "--enable-automation" not in serialized
    assert "automationcontrolled" not in serialized
    assert "undetected" not in serialized


def test_manual_login_does_not_attach_playwright(tmp_path: Path) -> None:
    pool = FixtureChromePool()
    driver = SystemChromeGoogleSessionDriver(context_pool=pool)

    probe = driver.open_login(
        "profile-0123456789ab",
        tmp_path / "browser-data",
        timeout_ms=20_000,
    )

    assert probe.state is GoogleSessionState.NEEDS_LOGIN
    assert "Google Chrome normal" in probe.detail
    assert len(pool.manual_calls) == 1
    assert pool.page_calls == 0


def test_find_google_chrome_prefers_known_windows_install_location(tmp_path: Path) -> None:
    local = tmp_path / "Local"
    chrome = local / "Google" / "Chrome" / "Application" / "chrome.exe"
    chrome.parent.mkdir(parents=True)
    chrome.write_bytes(b"fixture")

    found = find_google_chrome_executable(
        environ={
            "LOCALAPPDATA": str(local),
            "PROGRAMFILES": str(tmp_path / "ProgramFiles"),
            "PROGRAMFILES(X86)": str(tmp_path / "ProgramFilesX86"),
            "PATH": "",
        }
    )

    assert found == chrome.resolve()


def test_read_devtools_active_port_validates_profile_file(tmp_path: Path) -> None:
    (tmp_path / "DevToolsActivePort").write_text(
        "43127\n/devtools/browser/test\n", encoding="utf-8"
    )
    assert read_devtools_active_port(tmp_path) == 43127

    (tmp_path / "DevToolsActivePort").write_text("0\n", encoding="utf-8")
    with pytest.raises(FlowOtomatisError):
        read_devtools_active_port(tmp_path)
