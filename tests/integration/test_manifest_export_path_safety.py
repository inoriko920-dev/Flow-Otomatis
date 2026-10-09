"""Project result manifest must never write through redirected directory paths."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.result import ProjectResults
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter
from test_result_manifest_atomic_writes import _results


def _link_directory(link: Path, destination: Path) -> None:
    try:
        link.symlink_to(destination, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Directory symlinks unavailable on this Windows runner: {exc}")


def test_rejects_traversal_and_backslash_in_episode_before_any_write(tmp_path: Path) -> None:
    writer = ResultManifestWriter(tmp_path / "projects")
    for unsafe_id in ("../outside", "..", "EP\\..\\outside", "/outside", "EP/other"):
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

    def swap_before_commit(episode_id: str) -> Path:
        nonlocal checks
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
        return original(episode_id)

    monkeypatch.setattr(writer, "_verified_export_directory", swap_before_commit)
    with pytest.raises(InternalInvariantError, match="redirects"):
        writer.write(_results("after"))
    assert checks == 2
    assert not list(external.iterdir())
    safe = base / "EP_EXPORT_RACE" / "exports.safe"
    assert json.loads((safe / "FLOW_OTOMATIS_RESULT.json").read_text()) == previous
    assert not list(safe.glob("*.tmp"))
