"""Project result manifest must never write through redirected directory paths."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from flow_otomatis.domain.errors import InternalInvariantError
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
                target_duration_s=4.0,
                selected_flow_duration_s=4,
                trim_target_s=4.0,
                generate_state=None,
                remote_result_id=None,
                download_state=DownloadState.NOT_DOWNLOADED,
                output_path=None,
                take=1,
                updated_at=None,
            ),
        ),
    )


def _link_directory(link: Path, destination: Path) -> None:
    try:
        link.symlink_to(destination, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Directory symlinks unavailable on this Windows runner: {exc}")


def test_rejects_traversal_and_backslash_in_episode_before_any_write(tmp_path: Path) -> None:
    writer = ResultManifestWriter(tmp_path / "projects")
    for unsafe_id in (
        "../outside",
        "..",
        "EP\\..\\outside",
        "/outside",
        "EP/other",
        "C:outside",
        "EP:alternate-stream",
        "EP_TRAILING.",
        "EP_TRAILING ",
    ):
        with pytest.raises(InternalInvariantError, match="Unsafe episode identity"):
            writer.write(replace(_results("unsafe"), episode_id=unsafe_id))
    assert not (tmp_path / "outside").exists()
    assert not (tmp_path / "projects").exists()


def test_symlinked_exports_cannot_publish_outside_project(tmp_path: Path) -> None:
    base = tmp_path / "projects"
    project = base / "EP_EXPORT_RACE"
    project.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    _link_directory(project / "exports", external)
    writer = ResultManifestWriter(base)

    with pytest.raises(InternalInvariantError, match="redirects"):
        writer.write(_results("must-not-escape"))
    assert list(external.iterdir()) == []


def test_symlinked_project_cannot_create_exports_outside_root(tmp_path: Path) -> None:
    base = tmp_path / "projects"
    base.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    _link_directory(base / "EP_EXPORT_RACE", external)

    with pytest.raises(InternalInvariantError, match="redirects"):
        ResultManifestWriter(base).write(_results("must-not-escape"))
    assert not (external / "exports").exists()


def test_symlinked_existing_manifest_is_not_replaced(tmp_path: Path) -> None:
    base = tmp_path / "projects"
    export = base / "EP_EXPORT_RACE" / "exports"
    export.mkdir(parents=True)
    outside = tmp_path / "private.json"
    outside.write_text("secret-data", encoding="utf-8")
    try:
        (export / "FLOW_OTOMATIS_RESULT.json").symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"File symlinks unavailable on Windows runner: {exc}")

    with pytest.raises(InternalInvariantError, match="redirected file"):
        ResultManifestWriter(base).write(_results("do not replace"))
    assert outside.read_text(encoding="utf-8") == "secret-data"
    assert list(export.glob("*.tmp")) == []


def test_late_export_dir_swap_blocks_final_publish_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = tmp_path / "projects"
    writer = ResultManifestWriter(base)
    prior = writer.write(_results("before"))
    previous = json.loads(prior.read_text(encoding="utf-8"))
    original = writer._verified_export_directory
    external = tmp_path / "redirect"
    external.mkdir()
    checks = 0
    attacker_file: Path | None = None

    def swap_before_commit(episode_id: str) -> Path:
        nonlocal attacker_file, checks
        checks += 1
        if checks == 2:
            existing = base / episode_id / "exports"
            renamed = base / episode_id / "exports.safe"
            existing.rename(renamed)
            try:
                _link_directory(existing, external)
            except BaseException:
                renamed.rename(existing)
                raise
            # An attacker may deliberately place a same-named file on the
            # redirected parent. Cleanup must not erase that unrelated file.
            temporary_files = list(renamed.glob("*.tmp"))
            assert len(temporary_files) == 1
            attacker_file = external / temporary_files[0].name
            attacker_file.write_text("unrelated-external-file", encoding="utf-8")
        return original(episode_id)

    monkeypatch.setattr(writer, "_verified_export_directory", swap_before_commit)
    with pytest.raises(InternalInvariantError, match="redirects"):
        writer.write(_results("after"))
    assert checks == 2
    assert attacker_file is not None
    assert attacker_file.read_text(encoding="utf-8") == "unrelated-external-file"
    safe = base / "EP_EXPORT_RACE" / "exports.safe"
    assert json.loads((safe / "FLOW_OTOMATIS_RESULT.json").read_text()) == previous
    # The validated directory was renamed AFTER the tempfile was created.
    # Its private temporary moved with it. Never follow the now-redirected
    # original path to clean up: preserve this recovery file in the old,
    # trustworthy directory rather than risk unlinking an unrelated target.
    recovery = list(safe.glob("*.tmp"))
    assert len(recovery) == 1
    assert json.loads(recovery[0].read_text(encoding="utf-8"))["project_name"] == "after"


def test_rejects_simulated_ntfs_junction_redirect_even_without_symlink_privilege(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Windows resolve follows junctions that Path.is_symlink may not report."""

    base = tmp_path / "projects"
    root = base / "EP_EXPORT_RACE" / "exports"
    root.mkdir(parents=True)
    outside = tmp_path / "other-disk"
    outside.mkdir()
    original_resolve = Path.resolve

    def junction_resolve(self: Path, *, strict: bool = False) -> Path:
        if self == root:
            return outside
        return original_resolve(self, strict=strict)

    monkeypatch.setattr(Path, "resolve", junction_resolve)
    with pytest.raises(InternalInvariantError, match="redirects"):
        ResultManifestWriter(base).write(_results("no Windows junction"))
    assert not (root / "FLOW_OTOMATIS_RESULT.json").exists()
    assert not list(outside.iterdir())
