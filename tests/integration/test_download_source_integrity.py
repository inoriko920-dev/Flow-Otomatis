"""SOL09: offline source-image integrity around provider Download and cached MP4."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import zipfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

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


def _setup(tmp_path: Path, *, zip_source: bool = False, imported_baseline: bool = True) -> Rig:
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
        image_sha256_imported=(hashlib.sha256(_IMAGE).hexdigest() if imported_baseline else None),
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
        (source / "FLOW_OTOMATIS_IMPORT.json").write_text(json.dumps(manifest), encoding="utf-8")
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
        request_fingerprint=_scene_fingerprint(_EPISODE, scene, hashlib.sha256(_IMAGE).hexdigest()),
    )
    jobs.prepare_jobs([job])
    assert jobs.claim_next(_EPISODE, "source-test-owner", lease_seconds=60)
    jobs.mark_generated(job.job_id, "remote:source-verification", "source-test-owner")
    downloads = SqliteDownloadResultRepository(root)
    provider = FakeDownloadProvider()
    verifier = EpisodePackageReader()
    service = GeneratedMediaDownloadService(
        jobs,
        downloads,
        provider,
        root,
        workspace_repository=workspaces,
        image_verifier=verifier,
    )
    results = LocalResultsService(
        workspaces,
        jobs,
        downloads,
        ResultManifestWriter(root),
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
            jobs,
            downloads,
            provider,
            root,
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
        jobs,
        ChangeAfterSave(rig.root),
        rig.provider,
        rig.root,
        workspace_repository=workspaces,
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="source image"):
        service.download_scene(_EPISODE, _SCENE)
    stored = original.get(_EPISODE, _SCENE)
    assert stored is not None
    assert stored.state == DownloadState.DOWNLOADED
    assert Path(stored.output_path or "").read_bytes() == b"preserved-synthetic-mp4"
    assert not rig.results.snapshot(_EPISODE).handoff_ready


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol10_cache_image_mutates_during_download_row_lookup_no_false_success(
    tmp_path: Path, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    existing = rig.service.download_scene(_EPISODE, _SCENE)
    video = Path(existing.output_path or "")

    class ChangeImageDuringRead(SqliteDownloadResultRepository):
        def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
            record = super().get(episode_id, scene_id)
            _change_image(rig.source)
            return record

    workspaces = SqliteWorkspaceRepository(rig.root)
    service = GeneratedMediaDownloadService(
        SqliteGenerationJobRepository(rig.root),
        ChangeImageDuringRead(rig.root),
        rig.provider,
        rig.root,
        workspace_repository=workspaces,
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="source image"):
        service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 1
    assert rig.downloads.get(_EPISODE, _SCENE) == existing
    assert video.read_bytes() == b"preserved-synthetic-mp4"
    assert not rig.results.snapshot(_EPISODE).handoff_ready


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol10_image_mutates_during_empty_history_lookup_provider_not_called(
    tmp_path: Path, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)

    class ChangeImageDuringRead(SqliteDownloadResultRepository):
        def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
            record = super().get(episode_id, scene_id)
            assert record is None
            _change_image(rig.source)
            return record

    service = GeneratedMediaDownloadService(
        SqliteGenerationJobRepository(rig.root),
        ChangeImageDuringRead(rig.root),
        rig.provider,
        rig.root,
        workspace_repository=SqliteWorkspaceRepository(rig.root),
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="source image"):
        service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) is None
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()


@pytest.mark.parametrize("zip_source", [False, True])
@pytest.mark.parametrize("partial_name", ["attempt", "legacy"])
@pytest.mark.parametrize("partial_bytes", [b"", b"interrupted-browser-bytes"])
def test_sol11_crashed_browser_partial_without_sqlite_row_blocks_new_attempt(
    tmp_path: Path, zip_source: bool, partial_name: str, partial_bytes: bytes
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    folder = rig.root / _EPISODE / "downloads"
    folder.mkdir(parents=True)
    destination = folder / f"{_SCENE}__take_01.mp4"
    partial = (
        destination.with_name(f"{destination.name}.part")
        if partial_name == "legacy"
        else destination.with_name(f"{destination.name}.abandoned-worker.part")
    )
    partial.write_bytes(partial_bytes)

    with pytest.raises(InternalInvariantError, match="Prior Download partial file"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) is None
    assert partial.read_bytes() == partial_bytes
    assert not destination.exists()


def test_sol11_partial_from_interrupted_attempt_preserves_existing_failure_row(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    original_failure = DownloadRecord(
        episode_id=_EPISODE,
        scene_id=_SCENE,
        state=DownloadState.FAILED,
        updated_at=datetime.now(UTC),
        error_message="Previously confirmed safe failure",
        generation_remote_result_id="remote:source-verification",
    )
    rig.downloads.save_failure_if_unconfirmed(original_failure)
    folder = rig.root / _EPISODE / "downloads"
    folder.mkdir(parents=True)
    partial = folder / f"{_SCENE}__take_01.mp4.previous-worker.part"
    partial.write_bytes(b"unreconciled-partial")

    with pytest.raises(InternalInvariantError, match="Prior Download partial file"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) == original_failure
    assert partial.read_bytes() == b"unreconciled-partial"


def test_sol11_unrelated_partial_must_not_block_approved_scene(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    folder = rig.root / _EPISODE / "downloads"
    folder.mkdir(parents=True)
    unrelated = folder / "different-scene__take_01.mp4.other-worker.part"
    unrelated.write_bytes(b"unrelated-download")

    recorded = rig.service.download_scene(_EPISODE, _SCENE)

    assert rig.provider.calls == 1
    assert recorded.state == DownloadState.DOWNLOADED
    assert unrelated.read_bytes() == b"unrelated-download"
    assert rig.results.snapshot(_EPISODE).handoff_ready


def test_sol11_forged_review_message_without_sqlite_audit_cannot_bypass_partial_gate(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    # A copied status message is not equivalent to an atomic operator-review
    # transition and its immutable audit entry.
    forged = DownloadRecord(
        episode_id=_EPISODE,
        scene_id=_SCENE,
        state=DownloadState.FAILED,
        updated_at=datetime.now(UTC),
        error_message="Manual review completed; retry requires a separate explicit action.",
        generation_remote_result_id="remote:source-verification",
    )
    rig.downloads.save_failure_if_unconfirmed(forged)
    folder = rig.root / _EPISODE / "downloads"
    folder.mkdir(parents=True)
    partial = folder / f"{_SCENE}__take_01.mp4.unreviewed.part"
    partial.write_bytes(b"keep-unreviewed-evidence")

    assert rig.downloads.has_confirmed_manual_retry_authorization(forged) is False
    with pytest.raises(InternalInvariantError, match="Prior Download partial file"):
        rig.service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) == forged
    assert partial.read_bytes() == b"keep-unreviewed-evidence"


def _reviewed_retry(rig: Rig) -> DownloadRecord:
    ambiguous = DownloadRecord(
        episode_id=_EPISODE,
        scene_id=_SCENE,
        state=DownloadState.ATTENTION_REQUIRED,
        updated_at=datetime.now(UTC),
        error_message="Previous browser attempt uncertain; operator review required.",
        generation_remote_result_id="remote:source-verification",
    )
    rig.downloads.save_attention_if_unconfirmed(
        ambiguous, expected_remote_result_id="remote:source-verification"
    )
    released = rig.service.release_retry_after_manual_review(
        _EPISODE,
        _SCENE,
        expected_remote_result_id="remote:source-verification",
        expected_updated_at=ambiguous.updated_at.isoformat(),
        reviewed_provider_and_local_files=True,
    )
    assert released.state == DownloadState.FAILED
    return released


def test_sol12_review_authorizes_one_retry_and_second_attempt_needs_new_review(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    assert rig.downloads.has_confirmed_manual_retry_authorization(reviewed)

    generation = SqliteGenerationJobRepository(rig.root).list_for_episode(_EPISODE)[0]
    first_claim = rig.downloads.claim_reviewed_retry_if_present(
        reviewed, expected_generation=generation
    )
    assert first_claim is True
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed

    second_claim = rig.downloads.claim_reviewed_retry_if_present(
        reviewed, expected_generation=generation
    )
    assert second_claim is False
    renewed_attention = rig.downloads.get(_EPISODE, _SCENE)
    assert renewed_attention is not None
    assert renewed_attention.state == DownloadState.ATTENTION_REQUIRED
    assert "interrupted" in (renewed_attention.error_message or "")

    refreshed = rig.service.release_retry_after_manual_review(
        _EPISODE,
        _SCENE,
        expected_remote_result_id="remote:source-verification",
        expected_updated_at=renewed_attention.updated_at.isoformat(),
        reviewed_provider_and_local_files=True,
    )
    assert refreshed.state == DownloadState.FAILED
    assert refreshed.updated_at != reviewed.updated_at
    assert rig.downloads.has_confirmed_manual_retry_authorization(refreshed)

    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as conn:
        actions = [
            item[0]
            for item in conn.execute("SELECT action FROM download_reconciliation_audit ORDER BY id")
        ]
    assert actions == [
        "OPERATOR_REVIEWED_RETRY",
        "OPERATOR_REVIEWED_RETRY_CLAIMED",
        "OPERATOR_REVIEWED_RETRY",
    ]


@pytest.mark.parametrize("left_partial", [False, True])
def test_sol12_simulated_crash_after_claim_cannot_replay_review_on_restart(
    tmp_path: Path, left_partial: bool
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    preserved_partial = rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4.abandoned.part"

    class CrashingProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> GeneratedMediaDownloadResult:
            self.calls += 1
            if left_partial:
                preserved_partial.write_bytes(b"original-crashed-browser-evidence")
            # Simulates an abrupt process termination, bypassing normal
            # exception handling and leaving SQLite's FAILED row intact.
            raise SystemExit("simulated abrupt process termination")

    crashing = CrashingProvider()
    service = GeneratedMediaDownloadService(
        SqliteGenerationJobRepository(rig.root),
        rig.downloads,
        crashing,
        rig.root,
        workspace_repository=SqliteWorkspaceRepository(rig.root),
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(SystemExit, match="simulated abrupt process termination"):
        service.download_scene(_EPISODE, _SCENE)

    assert crashing.calls == 1
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    if left_partial:
        assert preserved_partial.read_bytes() == b"original-crashed-browser-evidence"

    # A separate service/repository instance models a newly started process.
    new_service = GeneratedMediaDownloadService(
        SqliteGenerationJobRepository(rig.root),
        SqliteDownloadResultRepository(rig.root),
        rig.provider,
        rig.root,
        workspace_repository=SqliteWorkspaceRepository(rig.root),
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        new_service.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0

    current = rig.downloads.get(_EPISODE, _SCENE)
    assert current is not None
    assert current.state == DownloadState.ATTENTION_REQUIRED
    if left_partial:
        assert preserved_partial.read_bytes() == b"original-crashed-browser-evidence"
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()


def test_sol12_two_connections_cannot_claim_the_same_review(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)

    def competing_claim() -> bool | None:
        separate = SqliteDownloadResultRepository(rig.root)
        generation = SqliteGenerationJobRepository(rig.root).list_for_episode(_EPISODE)[0]
        return separate.claim_reviewed_retry_if_present(reviewed, expected_generation=generation)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(competing_claim)
        second = pool.submit(competing_claim)
        outcomes = [first.result(timeout=15), second.result(timeout=15)]

    assert outcomes.count(True) == 1
    assert outcomes.count(False) == 1
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE).state == DownloadState.ATTENTION_REQUIRED
    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as conn:
        claims = conn.execute(
            """
            SELECT COUNT(*) FROM download_reconciliation_audit
            WHERE action = 'OPERATOR_REVIEWED_RETRY_CLAIMED'
            """
        ).fetchone()[0]
    assert claims == 1


def test_sol12_ordinary_failed_download_does_not_create_manual_retry_claim(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    plain_failure = DownloadRecord(
        episode_id=_EPISODE,
        scene_id=_SCENE,
        state=DownloadState.FAILED,
        updated_at=datetime.now(UTC),
        error_message="Safe failure before any provider transfer.",
        generation_remote_result_id="remote:source-verification",
    )
    rig.downloads.save_failure_if_unconfirmed(plain_failure)
    assert rig.service.download_scene(_EPISODE, _SCENE).state == DownloadState.DOWNLOADED
    assert rig.provider.calls == 1
    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as conn:
        audit_table = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE name = 'download_reconciliation_audit'
            """
        ).fetchone()
    assert audit_table is None


@pytest.mark.parametrize(
    "concurrent_change",
    [
        "generate_queued",
        "generate_remote_id",
        "generate_fingerprint",
        "generate_revision",
        "scene_duration",
        "scene_not_ready",
        "download_revision",
        "download_ambiguous",
    ],
)
def test_sol13_retry_claim_rejects_changed_sqlite_facts_before_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    concurrent_change: str,
) -> None:
    """Simulate another process mutating SQLite after the first Download read.

    A matching remote ID is insufficient if the prepared revision, Scene, or
    reviewed Download row changed. Reject without consuming the manual review.
    """

    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    database = rig.root / _EPISODE / "project.sqlite3"
    original_get = rig.downloads.get
    seen = False

    def stale_read_then_concurrent_commit(episode_id: str, scene_id: str) -> DownloadRecord | None:
        nonlocal seen
        record = original_get(episode_id, scene_id)
        if seen:
            return record
        seen = True
        changes = {
            "generate_queued": (
                "UPDATE generation_jobs SET state = 'QUEUED' WHERE scene_id = ?",
                (_SCENE,),
            ),
            "generate_remote_id": (
                "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
                ("remote:other-result", _SCENE),
            ),
            "generate_fingerprint": (
                "UPDATE generation_jobs SET request_fingerprint = ? WHERE scene_id = ?",
                ("different-prepared-request-revision", _SCENE),
            ),
            "generate_revision": (
                "UPDATE generation_jobs SET updated_at = ? WHERE scene_id = ?",
                ("2040-01-01T00:00:00+00:00", _SCENE),
            ),
            "scene_duration": (
                "UPDATE scenes SET selected_flow_duration_s = ? WHERE scene_id = ?",
                (6, _SCENE),
            ),
            "scene_not_ready": (
                "UPDATE scenes SET readiness = ? WHERE scene_id = ?",
                ("MISSING_IMAGE", _SCENE),
            ),
            "download_revision": (
                "UPDATE download_results SET updated_at = ? WHERE scene_id = ?",
                ("2040-01-01T00:00:00+00:00", _SCENE),
            ),
            "download_ambiguous": (
                "UPDATE download_results SET state = ? WHERE scene_id = ?",
                (DownloadState.ATTENTION_REQUIRED, _SCENE),
            ),
        }
        sql, args = changes[concurrent_change]
        with sqlite3.connect(database) as connection:
            connection.execute(sql, args)
            connection.commit()
        return record

    monkeypatch.setattr(rig.downloads, "get", stale_read_then_concurrent_commit)
    with pytest.raises(InternalInvariantError, match="manual reconciliation|source image"):
        rig.service.download_scene(_EPISODE, _SCENE)
    monkeypatch.setattr(rig.downloads, "get", original_get)

    assert seen
    assert rig.provider.calls == 0
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()
    with sqlite3.connect(database) as connection:
        actions = [
            row[0]
            for row in connection.execute(
                "SELECT action FROM download_reconciliation_audit ORDER BY id"
            )
        ]
    assert actions == ["OPERATOR_REVIEWED_RETRY"]
    stored = rig.downloads.get(_EPISODE, _SCENE)
    assert stored is not None
    if concurrent_change not in {"download_revision", "download_ambiguous"}:
        assert stored == reviewed


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol14_crash_between_claim_commit_and_provider_dispatch_requires_re_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, zip_source: bool
) -> None:
    """A crash at the exact dispatch boundary must not reuse one review."""

    rig = _setup(tmp_path, zip_source=zip_source)
    reviewed = _reviewed_retry(rig)
    assert rig.downloads.has_confirmed_manual_retry_authorization(reviewed)

    def crash_before_dispatch(**_kwargs: object) -> GeneratedMediaDownloadRequest:
        raise SystemExit("simulated crash before provider invocation")

    with monkeypatch.context() as patch:
        patch.setattr(
            "flow_otomatis.application.services.generated_media_download"
            ".GeneratedMediaDownloadRequest",
            crash_before_dispatch,
        )
        with pytest.raises(SystemExit, match="simulated crash before provider invocation"):
            rig.service.download_scene(_EPISODE, _SCENE)

    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as connection:
        actions = [
            row[0] for row in connection.execute("SELECT action FROM download_reconciliation_audit")
        ]
    assert actions == ["OPERATOR_REVIEWED_RETRY", "OPERATOR_REVIEWED_RETRY_CLAIMED"]

    restarted = GeneratedMediaDownloadService(
        SqliteGenerationJobRepository(rig.root),
        SqliteDownloadResultRepository(rig.root),
        rig.provider,
        rig.root,
        workspace_repository=SqliteWorkspaceRepository(rig.root),
        image_verifier=EpisodePackageReader(),
    )
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        restarted.download_scene(_EPISODE, _SCENE)
    assert rig.provider.calls == 0
    row = rig.downloads.get(_EPISODE, _SCENE)
    assert row is not None
    assert row.state == DownloadState.ATTENTION_REQUIRED
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()


@pytest.mark.parametrize("change", ["revision", "fingerprint"])
def test_sol14_generate_mutated_after_claim_before_provider_blocks_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    original_claim = rig.downloads.claim_reviewed_retry_if_present
    altered = False

    def commit_claim_then_change_generate(
        record: DownloadRecord, *, expected_generation: GenerationJob
    ) -> bool | None:
        nonlocal altered
        accepted = original_claim(record, expected_generation=expected_generation)
        if accepted is True:
            altered = True
            query = (
                "UPDATE generation_jobs SET updated_at = ? WHERE scene_id = ?"
                if change == "revision"
                else "UPDATE generation_jobs SET request_fingerprint = ? WHERE scene_id = ?"
            )
            new_value = (
                "2040-01-01T00:00:00+00:00" if change == "revision" else "altered-after-claim"
            )
            with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as connection:
                connection.execute(query, (new_value, _SCENE))
                connection.commit()
        return accepted

    monkeypatch.setattr(
        rig.downloads, "claim_reviewed_retry_if_present", commit_claim_then_change_generate
    )
    with pytest.raises(InternalInvariantError, match="Generate revision changed"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert altered
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()


@pytest.mark.parametrize("zip_source", [False, True])
def test_sol14_source_bytes_mutated_after_claim_before_provider_blocks_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, zip_source: bool
) -> None:
    rig = _setup(tmp_path, zip_source=zip_source)
    reviewed = _reviewed_retry(rig)
    original_claim = rig.downloads.claim_reviewed_retry_if_present
    altered = False

    def commit_claim_then_change_source(
        record: DownloadRecord, *, expected_generation: GenerationJob
    ) -> bool | None:
        nonlocal altered
        accepted = original_claim(record, expected_generation=expected_generation)
        if accepted is True:
            _change_image(rig.source)
            altered = True
        return accepted

    monkeypatch.setattr(
        rig.downloads, "claim_reviewed_retry_if_present", commit_claim_then_change_source
    )
    with pytest.raises(InternalInvariantError, match="source image"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert altered
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    assert not (rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4").exists()


def _replace_reviewed_download_state(
    root: Path, *, state: str, output_path: str | None = None
) -> None:
    """Simulate a competing process committing a newer Download revision."""

    with sqlite3.connect(root / _EPISODE / "project.sqlite3") as connection:
        connection.execute(
            """
            UPDATE download_results
            SET state = ?, updated_at = ?, output_path = ?, error_message = ?
            WHERE episode_id = ? AND scene_id = ?
            """,
            (
                state,
                "2040-01-01T00:00:00+00:00",
                output_path,
                "Competing process outcome; preserve for reconciliation.",
                _EPISODE,
                _SCENE,
            ),
        )
        connection.commit()


@pytest.mark.parametrize(
    "rival_state",
    [DownloadState.FAILED, DownloadState.ATTENTION_REQUIRED, DownloadState.DOWNLOADED],
)
def test_sol15_status_changed_after_claim_before_provider_rejects_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, rival_state: str
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    original_claim = rig.downloads.claim_reviewed_retry_if_present
    claimed = False

    def claim_then_commit_rival(
        record: DownloadRecord, *, expected_generation: GenerationJob
    ) -> bool | None:
        nonlocal claimed
        result = original_claim(record, expected_generation=expected_generation)
        if result is True:
            claimed = True
            _replace_reviewed_download_state(rig.root, state=rival_state)
        return result

    monkeypatch.setattr(rig.downloads, "claim_reviewed_retry_if_present", claim_then_commit_rival)
    with pytest.raises(InternalInvariantError, match="Download history changed"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert claimed
    assert rig.provider.calls == 0
    assert rig.downloads.get(_EPISODE, _SCENE).state == rival_state
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as connection:
        actions = [
            row[0]
            for row in connection.execute(
                "SELECT action FROM download_reconciliation_audit ORDER BY id"
            )
        ]
    assert actions == ["OPERATOR_REVIEWED_RETRY", "OPERATOR_REVIEWED_RETRY_CLAIMED"]


@pytest.mark.parametrize(
    "rival_state",
    [DownloadState.FAILED, DownloadState.ATTENTION_REQUIRED, DownloadState.DOWNLOADED],
)
def test_sol15_rival_status_during_provider_cannot_be_overwritten_by_mp4_save(
    tmp_path: Path, rival_state: str
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    video = rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4"
    rig.provider.on_download = lambda: _replace_reviewed_download_state(
        rig.root,
        state=rival_state,
        output_path=str(video) if rival_state == DownloadState.DOWNLOADED else None,
    )
    with pytest.raises(InternalInvariantError, match="atomic Download save"):
        rig.service.download_scene(_EPISODE, _SCENE)

    assert rig.provider.calls == 1
    assert video.read_bytes() == b"preserved-synthetic-mp4"
    stored = rig.downloads.get(_EPISODE, _SCENE)
    assert stored is not None
    assert stored.state == rival_state
    assert stored.updated_at.isoformat() == "2040-01-01T00:00:00+00:00"
    assert stored.error_message == "Competing process outcome; preserve for reconciliation."
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    with sqlite3.connect(rig.root / _EPISODE / "project.sqlite3") as connection:
        claim_count = connection.execute(
            """
            SELECT COUNT(*) FROM download_reconciliation_audit
            WHERE action = 'OPERATOR_REVIEWED_RETRY_CLAIMED'
            """
        ).fetchone()[0]
    assert claim_count == 1


def test_sol15_unmodified_reviewed_retry_can_finish_with_atomic_revision_guard(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)

    result = rig.service.download_scene(_EPISODE, _SCENE)

    assert result.state == DownloadState.DOWNLOADED
    assert rig.provider.calls == 1
    assert rig.downloads.get(_EPISODE, _SCENE) == result
    assert Path(result.output_path or "").read_bytes() == b"preserved-synthetic-mp4"
    assert not rig.downloads.has_confirmed_manual_retry_authorization(reviewed)


def test_sol15_claim_audit_required_even_when_review_row_fields_match(
    tmp_path: Path,
) -> None:
    rig = _setup(tmp_path)
    reviewed = _reviewed_retry(rig)
    job = SqliteGenerationJobRepository(rig.root).list_for_episode(_EPISODE)[0]
    attempted = DownloadRecord(
        episode_id=_EPISODE,
        scene_id=_SCENE,
        state=DownloadState.DOWNLOADED,
        updated_at=datetime.now(UTC),
        output_path=str(rig.root / _EPISODE / "downloads" / f"{_SCENE}__take_01.mp4"),
        generation_remote_result_id="remote:source-verification",
    )
    # A reviewed FAILED row by itself is not enough to fabricate a successful
    # retry: the matching one-shot claim must have committed first.
    assert (
        rig.downloads.save_if_current_generate(
            attempted,
            "remote:source-verification",
            expected_reviewed_download=reviewed,
        )
        is False
    )
    assert rig.downloads.get(_EPISODE, _SCENE) == reviewed
    assert rig.downloads.has_confirmed_manual_retry_authorization(reviewed)
    assert job.state == GenerationJobState.GENERATED
