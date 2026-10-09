"""Effective Download status must reject late junction and symlink redirection."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.application.file_integrity import is_available_output
from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import DownloadState, ProjectResults, SceneResult
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter
from flow_otomatis.presentation.results_view import verified_selected_mp4


def _ready_result(output: Path) -> ProjectResults:
    return ProjectResults(
        episode_id="EP_OUTPUT_GUARD",
        project_name="Safe MP4 handoff",
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            SceneResult(
                scene_id="SCENE_001",
                target_duration_s=4.0,
                selected_flow_duration_s=4,
                trim_target_s=4.0,
                generate_state=GenerationJobState.GENERATED,
                remote_result_id="fake:test-video",
                download_state=DownloadState.DOWNLOADED,
                output_path=str(output),
                take=1,
                updated_at=datetime.now(UTC),
            ),
        ),
    )


def test_normal_canonical_local_mp4_still_counts_as_downloaded(tmp_path: Path) -> None:
    mp4 = tmp_path / "clips" / "SCENE_001.mp4"
    mp4.parent.mkdir()
    mp4.write_bytes(b"local MP4 test bytes")
    assert is_available_output(str(mp4))
    results = _ready_result(mp4)
    assert results.handoff_ready
    assert verified_selected_mp4(results, "SCENE_001") == mp4.resolve()


def test_symlinked_ancestor_does_not_authorize_downloaded_or_handoff(
    tmp_path: Path,
) -> None:
    actual = tmp_path / "real"
    actual.mkdir()
    (actual / "SCENE_001.mp4").write_bytes(b"local video")
    alias = tmp_path / "redirect"
    try:
        alias.symlink_to(actual, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Symlink unavailable on Windows runner: {exc}")
    redirected = alias / "SCENE_001.mp4"
    assert redirected.is_file()
    assert not redirected.is_symlink()
    assert not is_available_output(str(redirected))

    project = _ready_result(redirected)
    assert verified_selected_mp4(project, "SCENE_001") is None
    manifest = ResultManifestWriter(tmp_path / "projects").write(project)
    row = json.loads(manifest.read_text(encoding="utf-8"))["scenes"][0]
    assert row["download_status"] == DownloadState.UNAVAILABLE


def test_simulated_windows_junction_is_rejected_without_symlink_privileges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "downloads"
    folder.mkdir()
    mp4 = folder / "SCENE_001.mp4"
    mp4.write_bytes(b"local video")
    other = tmp_path / "other"
    other.mkdir()
    actual_output = other / mp4.name
    actual_output.write_bytes(b"unrelated MP4")
    original_resolve = Path.resolve

    def junction_resolve(self: Path, *, strict: bool = False) -> Path:
        if self == mp4:
            return actual_output
        return original_resolve(self, strict=strict)

    assert is_available_output(str(mp4))
    monkeypatch.setattr(Path, "resolve", junction_resolve)
    assert not is_available_output(str(mp4))
    assert verified_selected_mp4(_ready_result(mp4), "SCENE_001") is None


def test_reverted_output_directory_restores_readonly_availability(tmp_path: Path) -> None:
    folder = tmp_path / "downloads"
    folder.mkdir()
    mp4 = folder / "SCENE_001.mp4"
    mp4.write_bytes(b"local bytes")
    assert is_available_output(str(mp4))
    moved = tmp_path / "downloads.safe"
    folder.rename(moved)
    assert not is_available_output(str(mp4))
    moved.rename(folder)
    assert is_available_output(str(mp4))
