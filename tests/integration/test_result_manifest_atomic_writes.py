"""Real filesystem regression for simultaneous and failed result-manifest exports."""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

import flow_otomatis.infrastructure.filesystem.result_manifest_writer as writer_module
from flow_otomatis.domain.result import DownloadState, ProjectResults, SceneResult
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter


def _results(project_name: str) -> ProjectResults:
    return ProjectResults(
        episode_id="EP_EXPORT_RACE",
        project_name=project_name,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            SceneResult(
                scene_id="SCENE_001",
                target_duration_s=3.8,
                selected_flow_duration_s=4,
                trim_target_s=3.8,
                generate_state=None,
                remote_result_id=None,
                download_state=DownloadState.NOT_DOWNLOADED,
                output_path=None,
                take=1,
                updated_at=None,
            ),
        ),
    )


def _leftovers(root: Path) -> list[Path]:
    return list((root / "EP_EXPORT_RACE" / "exports").glob("*.tmp"))


def test_concurrent_exports_have_unique_temporary_files_and_valid_final_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    writer = ResultManifestWriter(tmp_path)
    entered_first_publish = threading.Event()
    release_first_publish = threading.Event()
    original_replace = writer_module.os.replace
    staged: list[Path] = []

    def held_replace(src: str | Path, dst: str | Path) -> None:
        staged.append(Path(src))
        if len(staged) == 1:
            entered_first_publish.set()
            if not release_first_publish.wait(timeout=15):
                raise TimeoutError("First publisher did not resume")
        original_replace(src, dst)

    monkeypatch.setattr(writer_module.os, "replace", held_replace)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(writer.write, _results("First writer"))
        assert entered_first_publish.wait(timeout=15)
        try:
            second = pool.submit(writer.write, _results("Second writer"))
            target = second.result(timeout=15)
        finally:
            release_first_publish.set()
        assert first.result(timeout=15) == target

    assert len(staged) == 2
    assert staged[0] != staged[1], "Each export must own a unique temporary"
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["project_name"] in {"First writer", "Second writer"}
    assert payload["scene_count"] == 1
    assert payload["scenes"][0]["scene_id"] == "SCENE_001"
    assert _leftovers(tmp_path) == []


def test_failed_publish_preserves_previous_manifest_and_removes_own_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    writer = ResultManifestWriter(tmp_path)
    target = writer.write(_results("Published successfully"))
    original = target.read_bytes()

    def fail_replace(_src: str | Path, _dst: str | Path) -> None:
        raise OSError("simulated disk-level publish failure")

    monkeypatch.setattr(writer_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="publish failure"):
        writer.write(replace(_results("Published successfully"), project_name="Failed update"))

    assert target.read_bytes() == original
    assert json.loads(target.read_text(encoding="utf-8"))["project_name"] == (
        "Published successfully"
    )
    assert _leftovers(tmp_path) == []


def test_failed_tempfile_write_preserves_previous_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    writer = ResultManifestWriter(tmp_path)
    target = writer.write(_results("Original"))
    original = target.read_bytes()
    real_named_temporary = writer_module.tempfile.NamedTemporaryFile

    class BrokenOutput:
        def __init__(self, stream: object) -> None:
            self.stream = stream

        def __enter__(self):
            self.stream.__enter__()
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        @property
        def name(self) -> str:
            return self.stream.name

        def write(self, _value: str) -> None:
            raise OSError("simulated partial write failure")

    def broken_temporary(**kwargs):
        return BrokenOutput(real_named_temporary(**kwargs))

    monkeypatch.setattr(writer_module.tempfile, "NamedTemporaryFile", broken_temporary)
    with pytest.raises(OSError, match="partial write"):
        writer.write(_results("Not published"))
    assert target.read_bytes() == original
    assert _leftovers(tmp_path) == []
