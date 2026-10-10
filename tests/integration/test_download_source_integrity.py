"""SOL09: offline source-image integrity around provider Download and cached MP4."""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

import pytest

from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadRequest,
    GeneratedMediaDownloadResult,
)
from flow_otomatis.application.services.generated_media_download import (
    GeneratedMediaDownloadService,
)
from flow_otomatis.application.services.local_generation_queue import _scene_fingerprint
from flow_otomatis.application.services.local_results import LocalResultsService
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.result import DownloadRecord, DownloadState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader, ResultManifestWriter
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)

_EPISODE = "EP900_INTEGRITY"
_SCENE = "SCENE_001"
_IMAGE = b"approved-original-image"


class FakeDownloadProvider:
    def __init__(self) -> None:
        self.calls = 0
        self.on_download: Callable[[], None] | None = None

    def download(self, request: GeneratedMediaDownloadRequest) -> GeneratedMediaDownloadResult:
        self.calls += 1
        target = Path(request.destination_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"preserved-synthetic-mp4")
        if self.on_download is not None:
            self.on_download()
        return GeneratedMediaDownloadResult(output_path=str(target))


@dataclass(slots=True)
class Rig:
    service: GeneratedMediaDownloadService
    provider: FakeDownloadProvider
    downloads: SqliteDownloadResultRepository
    source: Path
    root: Path
    results: LocalResultsService


def _setup(
    tmp_path: Path, *, zip_source: bool = False, imported_baseline: bool = True
) -> Rig:
    now = datetime.now(UTC)
    scene = WorkspaceScene(
        scene_id=_SCENE,
        image_file=f"{_SCENE}.png",
        image_exists=True,
        motion_prompt="Slow camera push.",
        target_duration_s=4.0,
        recommended_flow_duration_s=4,
        selected_flow_duration_s=4,
        readiness=SceneReadiness.READY,
        trim_target_s=4.0,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        image_sha256_imported=(
            hashlib.sha256(_IMAGE).hexdigest() if imported_baseline else None
        ),
    )
    manifest = {
        "schema_version": "1.0",
        "episode_id": _EPISODE,
        "project_name": "Source Integrity",
        "production_profile": {
            "model": scene.model,
            "resolution": scene.resolution,
            "aspect_ratio": scene.aspect_ratio,
        },
        "scene_count": 1,
        "scenes": [
            {
                "scene_id": scene.scene_id,
                "image_file": scene.image_file,
                "motion_prompt": scene.motion_prompt,
                "target_duration_s": scene.target_duration_s,
                "recommended_flow_duration_s": scene.recommended_flow_duration_s,
                "selected_flow_duration_s": scene.selected_flow_duration_s,
                "trim_target_s": scene.trim_target_s,
                "model": scene.model,
                "resolution": scene.resolution,
                "aspect_ratio": scene.aspect_ratio,
                "status": "READY",
            }
        ],
        "created_at": now.isoformat(),
        "source_versions": {},
    }
    if zip_source:
        source = tmp_path / "source.zip"
        with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("FLOW_OTOMATIS_IMPORT.json", json.dumps(manifest))
            archive.writestr(scene.image_file, _IMAGE)
    else:
        source = tmp_path / "source"
        source.mkdir()
        (source / "FLOW_OTOMATIS_IMPORT.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (source / scene.image_file).write_bytes(_IMAGE)

    workspace = WorkspaceState(
        schema_version="1.0",
        episode_id=_EPISODE,
        project_name="Source Integrity",
        source_package_path=str(source),
        created_at=now,
        imported_at=now,
        model=scene.model,
        resolution=scene.resolution,
        aspect_ratio=scene.aspect_ratio,
        scenes=(scene,),
    )
    root = tmp_path / "projects"
    workspaces = SqliteWorkspaceRepository(root)
    workspaces.save(workspace)
    jobs = SqliteGenerationJobRepository(root)
    job = GenerationJob(
        job_id=f"{_EPISODE}:{_SCENE}:GENERATE",
        episode_id=_EPISODE,
        scene_id=_SCENE,
        target_duration_s=4,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file=scene.image_file,
        motion_prompt=scene.motion_prompt,
        model=scene.model,
        resolution=scene.resolution,
        aspect_ratio=scene.aspect_ratio,
        request_fingerprint=_scene_fingerprint(
            _EPISODE, scene, hashlib.sha256(_IMAGE).hexdigest()
        ),
    )
    jobs.prepare_jobs([job])
    assert jobs.claim_next(_EPISODE, "source-test-owner", lease_seconds=60)
    jobs.mark_generated(job.job_id, "remote:source-verification", "source-test-owner")
    downloads = SqliteDownloadResultRepository(root)
    provider = FakeDownloadProvider()
    verifier = EpisodePackageReader()
    service = GeneratedMediaDownloadService(
        jobs, downloads, provider, root,
        workspace_repository=workspaces,
        image_verifier=verifier,
    )
    results = LocalResultsService(
        workspaces, jobs, downloads, ResultManifestWriter(root),
        image_verifier=verifier,
    )
    return Rig(service, provider, downloads, source, root, results)


def _change_image(source: Path) -> None:
    if source.is_file():
        with zipfile.ZipFile(source) as archive:
            manifest = archive.read("FLOW_OTOMATIS_IMPORT.json")
        with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("FLOW_OTOMATIS_IMPORT.json", manifest)
            archive.writestr(f"{_SCENE}.png", b"different-image-same-name")
    else:
        (source / f"{_SCENE}.png").write_bytes(b"different-image-same-name")


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol09_unchanged_image_allows_real_offline_download_and_cached_return(
    tmp_path: Path, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    first = rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.service.download_scene(_EPISODE, _SCENE) == first
    assert rig.provider.calls == 1
    assert rig.results.snapshot(_EPISODE).handoff_ready


@pytest.mark.parametrize("zip_source", [False, True])
@pytest.mark.parametrize("imported_baseline", [False, True])
def test_sol09_changed_image_before_download_never_calls_provider(
    tmp_path: Path, zip_source: bool, imported_baseline: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source, imported_baseline=imported_baseline)
    _change_image(rig.source)
    with pytest.raises(InternalInvariantError, match="source image"):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) is None


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol09_cached_mp4_refuses_changed_source_without_destroying_history(
    tmp_path: Path, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    record = rig.service.download_scene(_EPISODE, _SCENE)
    video = Path(record.output_path or "")
    _change_image(rig.source)
    with pytest.raises(InternalInvariantError, match="source image"):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 1
    assert rig.downloads.get(_EPISODE, _SCENE) == record
    assert video.read_bytes() == b"preserved-synthetic-mp4"
    assert rig.results.snapshot(_EPISODE).handoff_ready is False


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol09_image_changed_during_provider_keeps_mp4_and_no_success_row(
    tmp_path: Path, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    rig.provider.on_download = lambda: _change_image(rig.source)
    with pytest.raises(InternalInvariantError, match="source image"):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 1
    assert rig.downloads.get(_EPISODE, _SCENE) is None
    video = rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4"
    assert video.read_bytes() == b"preserved-synthetic-mp4"
    with pytest.raises(InternalInvariantError):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 1


def test_sol09_source_disappears_even_when_workspace_metadata_still_ready(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    (rig.source / f"{_SCENE}.png").unlink()
    with pytest.raises(InternalInvariantError, match="source image"):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0


def test_sol09_partial_guard_dependencies_are_rejected(tmp_path: Path) -> None:
    root = tmp_path / "projects"
    jobs = SqliteGenerationJobRepository(root)
    downloads = SqliteDownloadResultRepository(root)
    provider = FakeDownloadProvider()
    with pytest.raises(ValueError, match="both Workspace and image verifier"):
        GeneratedMediaDownloadService(
            jobs, downloads, provider, root, image_verifier=EpisodePackageReader()
        )
    with pytest.raises(ValueError, match="both Workspace and image verifier"):
        GeneratedMediaDownloadService(
            jobs, downloads, provider, root,
            workspace_repository=SqliteWorkspaceRepository(root),
        )


def test_sol09_late_source_change_after_atomic_save_does_not_return_success(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    original = rig.downloads

    class ChangeAfterSave(SqliteDownloadResultRepository):
        def save_if_current_generate(
            self, record: DownloadRecord, expected_remote_result_id: str
        ) -> bool:
            saved = super().save_if_current_generate(record, expected_remote_result_id)
            if saved:
                _change_image(rig.source)
            return saved

    jobs = SqliteGenerationJobRepository(rig.root)
    workspaces = SqliteWorkspaceRepository(rig.root)
    service = GeneratedMediaDownloadService(
        jobs, ChangeAfterSave(rig.root), rig.provider, rig.root,
        workspace_repository=workspaces,
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="source image"):
        service.download_scene(_EPISODE, _SCENE)
    stored = original.get(_EPISODE, _SCENE)
    assert stored is not None
    assert stored.state is DownloadState.DOWNLOADED
    assert Path(stored.output_path or "").read_bytes() == b"preserved-synthetic-mp4"
    assert not rig.results.snapshot(_EPISODE).handoff_ready
