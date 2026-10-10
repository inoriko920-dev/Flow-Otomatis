from __future__ import annotations

import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier, Event

import pytest

from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadRequest,
    GeneratedMediaDownloadResult,
    MediaDownloadAmbiguousError,
    MediaDownloadAuthenticationRequiredError,
    MediaDownloadCancelledError,
    MediaDownloadProviderError,
)
from flow_otomatis.application.services.generated_media_download import (
    GeneratedMediaDownloadService,
)
from flow_otomatis.domain.errors import InternalInvariantError, StorageError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.result import DownloadRecord, DownloadState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)
from flow_otomatis.workers.browser.google_flow_download import (
    GoogleFlowDownloadEvidence,
    GoogleFlowDownloadProvider,
    GoogleFlowDownloadState,
)


def _workspace(episode_id: str = "EP500_DOWNLOAD") -> WorkspaceState:
    now = datetime.now(UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id=episode_id,
        project_name="Download Foundation",
        source_package_path="package.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            WorkspaceScene(
                scene_id="SCENE_001",
                image_file="SCENE_001.png",
                image_exists=True,
                motion_prompt="Slow push in.",
                target_duration_s=4.0,
                recommended_flow_duration_s=4,
                selected_flow_duration_s=4,
                readiness=SceneReadiness.READY,
                trim_target_s=4.0,
                model="Omni Flash 1.1",
                resolution="720p",
                aspect_ratio="16:9",
            ),
        ),
    )


def _generated_job(episode_id: str, scene_id: str) -> GenerationJob:
    now = datetime.now(UTC)
    return GenerationJob(
        job_id=f"{episode_id}:{scene_id}:GENERATE",
        episode_id=episode_id,
        scene_id=scene_id,
        target_duration_s=4.0,
        flow_duration_s=4,
        state=GenerationJobState.GENERATED,
        created_at=now,
        updated_at=now,
        image_file=f"{scene_id}.png",
        motion_prompt="Slow push in.",
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        request_fingerprint="verified-download-foundation",
        remote_result_id=f"remote:{scene_id}",
    )


class FakeDownloadDriver:
    def __init__(self, state: GoogleFlowDownloadState = GoogleFlowDownloadState.DOWNLOADED):
        self.state = state
        self.calls: list[tuple[str, str, str, int]] = []

    def download_one(
        self,
        profile_id: str,
        remote_result_id: str,
        destination_path: str,
        *,
        timeout_ms: int,
    ) -> GoogleFlowDownloadEvidence:
        self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
        if self.state is GoogleFlowDownloadState.DOWNLOADED:
            path = Path(destination_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake-video")
            return GoogleFlowDownloadEvidence(
                state=self.state,
                detail="fixture download complete",
                output_path=str(path),
            )
        return GoogleFlowDownloadEvidence(
            state=self.state,
            detail=f"fixture {self.state.value.lower()}",
        )


def _setup(tmp_path: Path, driver: FakeDownloadDriver):
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    jobs = SqliteGenerationJobRepository(projects_root)
    jobs.prepare_jobs([_generated_job("EP500_DOWNLOAD", "SCENE_001")])
    # prepare_jobs never overwrites a confirmed terminal GENERATED job, so insert it directly
    with __import__("sqlite3").connect(
        projects_root / "EP500_DOWNLOAD" / "project.sqlite3"
    ) as connection:
        connection.execute(
            """
            UPDATE generation_jobs
            SET state = ?, remote_result_id = ?
            WHERE job_id = ?
            """,
            (
                GenerationJobState.GENERATED.value,
                "remote:SCENE_001",
                "EP500_DOWNLOAD:SCENE_001:GENERATE",
            ),
        )
        connection.commit()
    downloads = SqliteDownloadResultRepository(projects_root)
    provider = GoogleFlowDownloadProvider("profile-safe", driver)
    service = GeneratedMediaDownloadService(jobs, downloads, provider, projects_root)
    return projects_root, jobs, downloads, service


def test_generated_scene_download_is_atomic_and_idempotent(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    projects_root, _jobs, downloads, service = _setup(tmp_path, driver)

    record = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    output = Path(record.output_path or "")

    assert record.state == DownloadState.DOWNLOADED
    assert output.is_file()
    assert output.read_bytes() == b"fake-video"
    assert output.name == "SCENE_001__take_01.mp4"
    assert not output.with_name(output.name + ".part").exists()
    assert len(driver.calls) == 1
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == record

    again = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert again == record
    assert len(driver.calls) == 1
    assert output.is_relative_to(projects_root.resolve())


@pytest.mark.parametrize(
    "change",
    ["queued_generate", "new_generate_id", "download_revision", "ambiguous_download"],
)
def test_cached_mp4_reuse_rechecks_both_rows_after_first_service_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    """A stale in-memory job or Download row never authorizes cached MP4 reuse."""

    import hashlib
    import sqlite3

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    video = Path(original.output_path or "")
    before_bytes = video.read_bytes()
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"
    initial_calls = len(driver.calls)

    original_get = downloads.get

    def race_after_get(episode_id: str, scene_id: str):
        current = original_get(episode_id, scene_id)
        with sqlite3.connect(database) as connection:
            if change == "queued_generate":
                connection.execute(
                    "UPDATE generation_jobs SET state = ? WHERE scene_id = ?",
                    (GenerationJobState.QUEUED.value, scene_id),
                )
            elif change == "new_generate_id":
                connection.execute(
                    "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
                    ("remote:REPLACEMENT", scene_id),
                )
            elif change == "download_revision":
                connection.execute(
                    "UPDATE download_results SET updated_at = ? WHERE scene_id = ?",
                    ("2040-01-01T00:00:00+00:00", scene_id),
                )
            else:
                connection.execute(
                    "UPDATE download_results SET state = ? WHERE scene_id = ?",
                    (DownloadState.ATTENTION_REQUIRED, scene_id),
                )
            connection.commit()
        return current

    monkeypatch.setattr(downloads, "get", race_after_get)
    with pytest.raises(InternalInvariantError, match="Cached Download no longer matches"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == initial_calls
    assert video.read_bytes() == before_bytes

    monkeypatch.setattr(downloads, "get", original_get)
    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert hashlib.sha256(video.read_bytes()).digest() == hashlib.sha256(before_bytes).digest()
    if change == "download_revision":
        assert stored.updated_at.isoformat() == "2040-01-01T00:00:00+00:00"
    elif change == "ambiguous_download":
        assert stored.state == DownloadState.ATTENTION_REQUIRED
    else:
        assert stored == original


def test_f03_cached_mp4_refuses_old_scene_duration_without_touching_history(
    tmp_path: Path,
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    recorded = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    mp4 = Path(recorded.output_path or "")
    original_bytes = mp4.read_bytes()
    workspace_repo = SqliteWorkspaceRepository(root)
    workspace = workspace_repo.load("EP500_DOWNLOAD")
    assert workspace is not None
    revised = replace(
        workspace,
        scenes=(replace(workspace.scenes[0], selected_flow_duration_s=6),),
    )
    workspace_repo.update(revised, expected_workspace=workspace)

    with pytest.raises(InternalInvariantError, match="Cached Download no longer matches"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == recorded
    assert mp4.read_bytes() == original_bytes


@pytest.mark.parametrize(
    "scene_change",
    [
        {"image_exists": False, "readiness": SceneReadiness.MISSING_IMAGE},
        {"readiness": SceneReadiness.MISSING_PROMPT},
    ],
)
def test_f03_cached_video_is_not_reused_when_scene_is_not_ready(
    tmp_path: Path, scene_change: dict[str, object]
) -> None:
    driver = FakeDownloadDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)
    recorded = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    video = Path(recorded.output_path or "")
    original = video.read_bytes()
    workspace_repo = SqliteWorkspaceRepository(root)
    workspace = workspace_repo.load("EP500_DOWNLOAD")
    assert workspace is not None
    updated = replace(workspace.scenes[0], **scene_change)
    workspace_repo.update(
        replace(workspace, scenes=(updated,)), expected_workspace=workspace
    )
    assert downloads.matches_current_generated_download(recorded) is False
    with pytest.raises(InternalInvariantError, match="Cached Download no longer matches"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == recorded
    assert video.read_bytes() == original
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].state is GenerationJobState.GENERATED


def test_cached_mp4_identity_guard_reads_sqlite_without_writes(tmp_path: Path) -> None:
    """An ordinary idempotent Download read must not alter successful SQLite history."""

    import hashlib

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"
    before = hashlib.sha256(database.read_bytes()).hexdigest()

    assert downloads.matches_current_generated_download(original)
    assert service.download_scene("EP500_DOWNLOAD", "SCENE_001") == original
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before
    assert len(driver.calls) == 1


@pytest.mark.parametrize(
    "reported_state",
    [GoogleFlowDownloadState.SAFE_FAILURE, GoogleFlowDownloadState.AMBIGUOUS],
)
@pytest.mark.parametrize("change", ["requeued", "replaced_remote_id"])
def test_stale_browser_outcome_cannot_poison_new_generate_result(
    tmp_path: Path,
    reported_state: GoogleFlowDownloadState,
    change: str,
) -> None:
    """A late failure/ambiguity is not a failure of a newer Generate result."""

    import sqlite3

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"

    class StaleBrowserDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            if reported_state is GoogleFlowDownloadState.AMBIGUOUS:
                Path(destination_path).write_bytes(b"previous-generate-uncertain-partial")
            with sqlite3.connect(database) as connection:
                if change == "requeued":
                    connection.execute(
                        "UPDATE generation_jobs SET state = ? WHERE scene_id = ?",
                        (GenerationJobState.QUEUED.value, "SCENE_001"),
                    )
                else:
                    connection.execute(
                        "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
                        ("remote:NEW_GENERATE", "SCENE_001"),
                    )
                connection.commit()
            return evidence

    driver = StaleBrowserDriver(reported_state)
    service._provider = GoogleFlowDownloadProvider("profile-safe", driver)
    expected_error = (
        MediaDownloadAmbiguousError
        if reported_state is GoogleFlowDownloadState.AMBIGUOUS
        else MediaDownloadProviderError
    )
    with pytest.raises(expected_error):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    # A stale failure or sticky ambiguity cannot be written as the outcome
    # for the new generation ID, even though the worker did run once.
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert len(driver.calls) == 1
    with sqlite3.connect(database) as connection:
        current = connection.execute(
            "SELECT state, remote_result_id FROM generation_jobs WHERE scene_id = ?",
            ("SCENE_001",),
        ).fetchone()
    assert current == (
        (GenerationJobState.QUEUED.value, "remote:SCENE_001")
        if change == "requeued"
        else (GenerationJobState.GENERATED.value, "remote:NEW_GENERATE")
    )
    partials = list((root / "EP500_DOWNLOAD" / "downloads").glob("*.part"))
    assert len(partials) == int(reported_state is GoogleFlowDownloadState.AMBIGUOUS)
    if partials:
        assert partials[0].read_bytes() == b"previous-generate-uncertain-partial"


def test_download_requires_generated_state_and_never_starts_generate(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    _root, jobs, _downloads, service = _setup(tmp_path, driver)
    db = tmp_path / "projects" / "EP500_DOWNLOAD" / "project.sqlite3"

    with __import__("sqlite3").connect(db) as connection:
        connection.execute(
            "UPDATE generation_jobs SET state = ?, remote_result_id = NULL",
            (GenerationJobState.QUEUED.value,),
        )
        connection.commit()

    with pytest.raises(InternalInvariantError, match="GENERATED"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert driver.calls == []
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].state is GenerationJobState.QUEUED


@pytest.mark.parametrize(
    "state",
    [
        GoogleFlowDownloadState.SAFE_FAILURE,
        GoogleFlowDownloadState.CANCELLED,
        GoogleFlowDownloadState.AUTH_REQUIRED,
    ],
)
@pytest.mark.parametrize("output_kind", ["external", "blank"])
def test_contradictory_failure_evidence_requires_review_before_retry(
    tmp_path: Path,
    state: GoogleFlowDownloadState,
    output_kind: str,
) -> None:
    """Non-success with a named output is unconfirmed, not safely retryable."""

    outside = tmp_path / "DO_NOT_PERSIST-outside.mp4"
    outside.write_bytes(b"unrelated-file-preserved")

    class ContradictoryDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            return GoogleFlowDownloadEvidence(
                state=state,
                detail="access_token=DO_NOT_PERSIST",
                output_path=str(outside) if output_kind == "external" else "",
            )

    driver = ContradictoryDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="conflicting Download evidence"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    current = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert current is not None
    assert current.state == DownloadState.ATTENTION_REQUIRED
    assert current.generation_remote_result_id == "remote:SCENE_001"
    assert current.output_path is None
    assert "DO_NOT_PERSIST" not in (current.error_message or "")
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()
    assert outside.read_bytes() == b"unrelated-file-preserved"
    assert not (root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4").exists()
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1


@pytest.mark.parametrize(
    ("state", "error_type", "expected_state"),
    [
        (
            GoogleFlowDownloadState.AUTH_REQUIRED,
            MediaDownloadAuthenticationRequiredError,
            DownloadState.FAILED,
        ),
        (
            GoogleFlowDownloadState.AMBIGUOUS,
            MediaDownloadAmbiguousError,
            DownloadState.ATTENTION_REQUIRED,
        ),
    ],
)
def test_controlled_download_failure_records_failure_without_retry(
    tmp_path: Path,
    state: GoogleFlowDownloadState,
    error_type: type[Exception],
    expected_state: str,
) -> None:
    driver = FakeDownloadDriver(state)
    _root, _jobs, downloads, service = _setup(tmp_path, driver)

    with pytest.raises(error_type):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert len(driver.calls) == 1
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == expected_state
    assert record.output_path is None
    if state is GoogleFlowDownloadState.AMBIGUOUS:
        assert record.generation_remote_result_id == "remote:SCENE_001"
        with pytest.raises(InternalInvariantError, match="manual reconciliation"):
            service.download_scene("EP500_DOWNLOAD", "SCENE_001")
        assert len(driver.calls) == 1


@pytest.mark.parametrize(
    ("state", "error_type", "expected_state"),
    [
        (GoogleFlowDownloadState.SAFE_FAILURE, MediaDownloadProviderError, DownloadState.FAILED),
        (
            GoogleFlowDownloadState.AUTH_REQUIRED,
            MediaDownloadAuthenticationRequiredError,
            DownloadState.FAILED,
        ),
        (GoogleFlowDownloadState.CANCELLED, MediaDownloadCancelledError, DownloadState.FAILED),
        (
            GoogleFlowDownloadState.AMBIGUOUS,
            MediaDownloadAmbiguousError,
            DownloadState.ATTENTION_REQUIRED,
        ),
    ],
)
def test_browser_evidence_detail_never_enters_errors_or_sqlite(
    tmp_path: Path,
    state: GoogleFlowDownloadState,
    error_type: type[Exception],
    expected_state: str,
) -> None:
    """Sanitized driver evidence cannot leak private session URLs into history."""

    class SecretEvidenceDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            return GoogleFlowDownloadEvidence(
                state=state,
                detail="https://example.invalid/?access_token=DO_NOT_PERSIST",
            )

    driver = SecretEvidenceDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(error_type) as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(raised.value)
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == expected_state
    assert record.error_message
    assert "DO_NOT_PERSIST" not in record.error_message
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"
    assert b"DO_NOT_PERSIST" not in database.read_bytes()
    assert len(driver.calls) == 1


@pytest.mark.parametrize(
    ("error_type", "expected_state"),
    [
        (MediaDownloadProviderError, DownloadState.FAILED),
        (MediaDownloadAuthenticationRequiredError, DownloadState.FAILED),
        (MediaDownloadCancelledError, DownloadState.FAILED),
        (MediaDownloadAmbiguousError, DownloadState.ATTENTION_REQUIRED),
    ],
)
def test_browser_driver_typed_exception_text_never_leaks(
    tmp_path: Path,
    error_type: type[MediaDownloadProviderError],
    expected_state: str,
) -> None:
    """Keep typed errors while discarding untrusted driver exception strings."""

    class SecretErrorDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            raise error_type("private-browser-cookie=DO_NOT_PERSIST")

    driver = SecretErrorDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(error_type) as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(raised.value)
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == expected_state
    assert record.error_message
    assert "DO_NOT_PERSIST" not in record.error_message
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()
    assert len(driver.calls) == 1


@pytest.mark.parametrize("error_class", [TimeoutError, OSError, RuntimeError])
@pytest.mark.parametrize("leave_final_mp4", [False, True])
def test_unexpected_alternate_provider_crash_is_sticky_and_preserves_bytes(
    tmp_path: Path,
    error_class: type[Exception],
    leave_final_mp4: bool,
) -> None:
    """The service enforces fail-closed semantics for *any* Download provider."""

    class CrashingProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            self.calls += 1
            if leave_final_mp4:
                destination = Path(request.destination_path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"uncertain-final-mp4")
            raise error_class("private-browser-cookie=DO_NOT_PERSIST")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    provider = CrashingProvider()
    service._provider = provider  # type: ignore[assignment]

    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation") as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(raised.value)

    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == "remote:SCENE_001"
    assert stored.output_path is None
    assert "DO_NOT_PERSIST" not in (stored.error_message or "")
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()

    final_mp4 = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final_mp4.exists() is leave_final_mp4
    if leave_final_mp4:
        assert final_mp4.read_bytes() == b"uncertain-final-mp4"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert provider.calls == 1
    if leave_final_mp4:
        assert final_mp4.read_bytes() == b"uncertain-final-mp4"


@pytest.mark.parametrize(
    "variant",
    ["none", "wrong_object", "blank_path", "wrong_path_type", "nul_path"],
)
@pytest.mark.parametrize("leave_final_mp4", [False, True])
def test_untrusted_provider_malformed_success_is_sticky_and_preserves_mp4(
    tmp_path: Path,
    variant: str,
    leave_final_mp4: bool,
) -> None:
    """A malformed provider result cannot trigger an unreviewed second request."""

    class MalformedProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> object:
            self.calls += 1
            if leave_final_mp4:
                path = Path(request.destination_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unconfirmed-download")
            if variant == "none":
                return None
            if variant == "wrong_object":
                return object()
            if variant == "blank_path":
                return GeneratedMediaDownloadResult(output_path=" ")
            if variant == "wrong_path_type":
                return GeneratedMediaDownloadResult(output_path=123)  # type: ignore[arg-type]
            return GeneratedMediaDownloadResult(output_path=chr(0))

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    provider = MalformedProvider()
    service._provider = provider  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAmbiguousError, match="invalid success evidence"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.ATTENTION_REQUIRED
    assert recorded.generation_remote_result_id == "remote:SCENE_001"
    assert recorded.output_path is None
    assert recorded.take == 1
    assert "invalid success evidence" in (recorded.error_message or "")

    output = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert output.exists() is leave_final_mp4
    if leave_final_mp4:
        assert output.read_bytes() == b"unconfirmed-download"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert provider.calls == 1
    if leave_final_mp4:
        assert output.read_bytes() == b"unconfirmed-download"


def test_unexpected_provider_crash_does_not_replace_rival_confirmed_download(
    tmp_path: Path,
) -> None:
    """A concurrent confirmed MP4 must survive an older provider's crash."""

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    original_provider = service._provider

    class RacingProvider:
        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            original_provider.download(request)
            # Simulate a different process committing the confirmed result
            # before this provider's uncertain exception returns.
            saved = DownloadRecord(
                episode_id=request.episode_id,
                scene_id=request.scene_id,
                state=DownloadState.DOWNLOADED,
                updated_at=datetime.now(UTC),
                output_path=request.destination_path,
                take=1,
                generation_remote_result_id=request.remote_result_id,
            )
            assert downloads.save_if_current_generate(saved, request.remote_result_id)
            raise RuntimeError("private-token=DO_NOT_PERSIST")

    service._provider = RacingProvider()  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.DOWNLOADED
    final_mp4 = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final_mp4.read_bytes() == b"fake-video"
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()


@pytest.mark.parametrize(
    "error_type",
    [
        MediaDownloadProviderError,
        MediaDownloadAuthenticationRequiredError,
        MediaDownloadCancelledError,
        MediaDownloadAmbiguousError,
    ],
)
def test_typed_provider_error_with_published_mp4_requires_manual_reconciliation(
    tmp_path: Path,
    error_type: type[MediaDownloadProviderError],
) -> None:
    """Never mark a written MP4 as safely failed, regardless of provider error type."""

    class FailedAfterWritingProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            self.calls += 1
            destination = Path(request.destination_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"published-before-typed-error")
            raise error_type("private-browser-token=DO_NOT_PERSIST")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    provider = FailedAfterWritingProvider()
    service._provider = provider  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAmbiguousError, match="reconciliation") as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(raised.value)
    saved = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert saved is not None
    assert saved.state == DownloadState.ATTENTION_REQUIRED
    assert saved.output_path is None
    assert saved.generation_remote_result_id == "remote:SCENE_001"
    assert "DO_NOT_PERSIST" not in (saved.error_message or "")
    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final.read_bytes() == b"published-before-typed-error"
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert provider.calls == 1
    assert final.read_bytes() == b"published-before-typed-error"


@pytest.mark.parametrize(
    "error_type",
    [
        MediaDownloadProviderError,
        MediaDownloadAuthenticationRequiredError,
        MediaDownloadCancelledError,
    ],
)
@pytest.mark.parametrize("partial_contents", [b"", b"uncertain-browser-transfer"])
def test_alternate_provider_typed_failure_with_partial_requires_review(
    tmp_path: Path,
    error_type: type[MediaDownloadProviderError],
    partial_contents: bytes,
) -> None:
    """A typed safe error cannot hide attempt-owned temporary Download evidence."""

    class PartialThenFailedProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            self.calls += 1
            final = Path(request.destination_path)
            partial = final.with_name(f"{final.name}.custom-attempt.part")
            partial.parent.mkdir(parents=True, exist_ok=True)
            partial.write_bytes(partial_contents)
            raise error_type("private-browser-session=DO_NOT_PERSIST")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    provider = PartialThenFailedProvider()
    service._provider = provider  # type: ignore[assignment]

    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation") as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(raised.value)
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == DownloadState.ATTENTION_REQUIRED
    assert record.generation_remote_result_id == "remote:SCENE_001"
    assert record.output_path is None
    assert "DO_NOT_PERSIST" not in (record.error_message or "")

    directory = root / "EP500_DOWNLOAD" / "downloads"
    final = directory / "SCENE_001__take_01.mp4"
    partial = directory / "SCENE_001__take_01.mp4.custom-attempt.part"
    assert not final.exists()
    assert partial.read_bytes() == partial_contents
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()

    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert provider.calls == 1
    assert partial.read_bytes() == partial_contents


@pytest.mark.parametrize("scene_id", ["SCENE_[001]", "SCENE_[AB]"])
def test_alternate_provider_partial_is_detected_for_literal_bracket_scene_names(
    tmp_path: Path,
    scene_id: str,
) -> None:
    """Glob metacharacters in a valid Scene ID cannot conceal its own partial."""

    import sqlite3

    class PartialFailureProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            self.calls += 1
            path = Path(request.destination_path)
            path.with_name(f"{path.name}.test-attempt.part").write_bytes(b"unconfirmed")
            raise MediaDownloadAuthenticationRequiredError("session expired")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    with sqlite3.connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as connection:
        connection.execute(
            "UPDATE generation_jobs SET scene_id = ?, remote_result_id = ? WHERE scene_id = ?",
            (scene_id, f"remote:{scene_id}", "SCENE_001"),
        )
        connection.commit()

    provider = PartialFailureProvider()
    service._provider = provider  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", scene_id)

    stored = downloads.get("EP500_DOWNLOAD", scene_id)
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == f"remote:{scene_id}"
    final = root / "EP500_DOWNLOAD" / "downloads" / f"{scene_id}__take_01.mp4"
    partial = final.with_name(f"{final.name}.test-attempt.part")
    assert partial.read_bytes() == b"unconfirmed"
    assert not final.exists()
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", scene_id)
    assert provider.calls == 1


def test_bracket_scene_name_does_not_match_unrelated_partial(
    tmp_path: Path,
) -> None:
    """Literal brackets must not accidentally match another Scene's part file."""

    import sqlite3

    scene_id = "SCENE_[01]"
    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    with sqlite3.connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as connection:
        connection.execute(
            "UPDATE generation_jobs SET scene_id = ?, remote_result_id = ? WHERE scene_id = ?",
            (scene_id, f"remote:{scene_id}", "SCENE_001"),
        )
        connection.commit()

    class UnrelatedPartProvider:
        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            final = Path(request.destination_path)
            (final.parent / "SCENE_0__take_01.mp4.other.part").write_bytes(b"unrelated")
            raise MediaDownloadAuthenticationRequiredError("manual login required")

    service._provider = UnrelatedPartProvider()  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAuthenticationRequiredError):
        service.download_scene("EP500_DOWNLOAD", scene_id)

    record = downloads.get("EP500_DOWNLOAD", scene_id)
    assert record is not None
    assert record.state == DownloadState.FAILED
    assert (
        root / "EP500_DOWNLOAD" / "downloads" / "SCENE_0__take_01.mp4.other.part"
    ).read_bytes() == b"unrelated"


def test_unrelated_partial_does_not_change_safe_failure_classification(
    tmp_path: Path,
) -> None:
    """Only this canonical MP4's partials are evidence for a given attempt."""

    class UnrelatedPartialProvider:
        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            destination = Path(request.destination_path)
            other = destination.parent / "different-scene.mp4.old.part"
            other.write_bytes(b"another-scene-evidence")
            raise MediaDownloadAuthenticationRequiredError("login required")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    service._provider = UnrelatedPartialProvider()  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAuthenticationRequiredError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == DownloadState.FAILED
    assert (
        root / "EP500_DOWNLOAD" / "downloads" / "different-scene.mp4.old.part"
    ).read_bytes() == b"another-scene-evidence"


def test_typed_provider_error_cannot_override_rival_success_at_same_destination(
    tmp_path: Path,
) -> None:
    """A confirmed rival download remains DOWNLOADED after a typed provider error."""

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())

    class RacingProvider:
        def download(self, request: GeneratedMediaDownloadRequest) -> None:
            destination = Path(request.destination_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"rival-confirmed-mp4")
            rival = DownloadRecord(
                episode_id=request.episode_id,
                scene_id=request.scene_id,
                state=DownloadState.DOWNLOADED,
                updated_at=datetime.now(UTC),
                output_path=str(destination),
                take=1,
                generation_remote_result_id=request.remote_result_id,
            )
            assert downloads.save_if_current_generate(rival, request.remote_result_id)
            raise MediaDownloadProviderError("private-token=DO_NOT_PERSIST")

    service._provider = RacingProvider()  # type: ignore[assignment]
    with pytest.raises(MediaDownloadAmbiguousError, match="reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.DOWNLOADED
    destination = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert recorded.output_path == str(destination)
    assert destination.read_bytes() == b"rival-confirmed-mp4"


@pytest.mark.parametrize(
    ("error_type", "expected_state"),
    [
        (MediaDownloadProviderError, DownloadState.FAILED),
        (MediaDownloadAuthenticationRequiredError, DownloadState.FAILED),
        (MediaDownloadAmbiguousError, DownloadState.ATTENTION_REQUIRED),
    ],
)
def test_download_service_redacts_custom_provider_error_on_sqlite_boundary(
    tmp_path: Path,
    error_type: type[MediaDownloadProviderError],
    expected_state: str,
) -> None:
    """A second provider implementation cannot bypass SQLite error redaction."""

    class UntrustedProvider:
        def download(self, request: GeneratedMediaDownloadRequest):
            del request
            raise error_type("session-token=DO_NOT_PERSIST")

    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    service._provider = UntrustedProvider()  # type: ignore[assignment]
    with pytest.raises(error_type):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == expected_state
    assert record.error_message
    assert "DO_NOT_PERSIST" not in record.error_message
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()


@pytest.mark.parametrize(
    "reported_state",
    [
        GoogleFlowDownloadState.SAFE_FAILURE,
        GoogleFlowDownloadState.CANCELLED,
        GoogleFlowDownloadState.AUTH_REQUIRED,
    ],
)
def test_driver_cannot_report_safe_outcome_after_leaving_partial(
    tmp_path: Path,
    reported_state: GoogleFlowDownloadState,
) -> None:
    """Preserve uncertain partial bytes and require review instead of retry."""

    class PartialThenSafeDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            path = Path(destination_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"uncertain-partial-from-browser")
            return evidence

    driver = PartialThenSafeDriver(reported_state)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="left a partial file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == "remote:SCENE_001"
    assert stored.output_path is None
    directory = root / "EP500_DOWNLOAD" / "downloads"
    partials = list(directory.glob("SCENE_001__take_01.mp4.*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"uncertain-partial-from-browser"
    assert not (directory / "SCENE_001__take_01.mp4").exists()

    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1
    assert partials[0].read_bytes() == b"uncertain-partial-from-browser"


def test_driver_exception_with_partial_requires_reconciliation(tmp_path: Path) -> None:
    """Even a typed safe exception cannot erase proof of a partial transfer."""

    class InterruptedDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            partial = Path(destination_path)
            partial.parent.mkdir(parents=True, exist_ok=True)
            partial.write_bytes(b"partial-before-auth-error")
            raise MediaDownloadProviderError("browser driver interrupted after writing")

    driver = InterruptedDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="left a partial file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    directory = root / "EP500_DOWNLOAD" / "downloads"
    partials = list(directory.glob("SCENE_001__take_01.mp4.*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"partial-before-auth-error"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1


@pytest.mark.parametrize("error_class", [TimeoutError, OSError, RuntimeError])
@pytest.mark.parametrize("leave_partial", [False, True])
def test_unexpected_browser_exception_requires_review_without_disclosing_details(
    tmp_path: Path,
    error_class: type[Exception],
    leave_partial: bool,
) -> None:
    """Unknown driver errors cannot silently authorize a second browser request."""

    class CrashedDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            if leave_partial:
                path = Path(destination_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unconfirmed-browser-transfer")
            raise error_class("sensitive-session-token=DO_NOT_PERSIST")

    driver = CrashedDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation") as raised:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert raised.value.__suppress_context__
    assert "DO_NOT_PERSIST" not in "".join(traceback.format_exception(raised.value))

    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.ATTENTION_REQUIRED
    assert recorded.generation_remote_result_id == "remote:SCENE_001"
    assert recorded.output_path is None
    assert "DO_NOT_PERSIST" not in (recorded.error_message or "")

    folder = root / "EP500_DOWNLOAD" / "downloads"
    partials = list(folder.glob("SCENE_001__take_01.mp4.*.part"))
    assert len(partials) == int(leave_partial)
    if leave_partial:
        assert partials[0].read_bytes() == b"unconfirmed-browser-transfer"
    assert not (folder / "SCENE_001__take_01.mp4").exists()

    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1
    if leave_partial:
        assert partials[0].read_bytes() == b"unconfirmed-browser-transfer"


def test_download_provider_rejects_untracked_existing_final_file(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    _root, _jobs, _downloads, service = _setup(tmp_path, driver)
    destination = tmp_path / "projects" / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"do-not-overwrite")

    with pytest.raises(InternalInvariantError, match="will not be overwritten"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert destination.read_bytes() == b"do-not-overwrite"
    assert driver.calls == []


@pytest.mark.parametrize(
    "malformed",
    [
        "none",
        "dictionary",
        "string_success",
        "unknown_state",
        "null_state",
        "numeric_success_path",
        "empty_success_path",
    ],
)
@pytest.mark.parametrize("leave_partial", [False, True])
def test_malformed_browser_evidence_never_authorizes_safe_retry(
    tmp_path: Path,
    malformed: str,
    leave_partial: bool,
) -> None:
    """Untrusted browser evidence is ambiguous even without visible partial bytes."""

    class MalformedEvidenceDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            self.calls.append((profile_id, remote_result_id, destination_path, timeout_ms))
            if leave_partial:
                partial = Path(destination_path)
                partial.parent.mkdir(parents=True, exist_ok=True)
                partial.write_bytes(b"unknown-browser-result")
            if malformed == "none":
                return None  # type: ignore[return-value]
            if malformed == "dictionary":
                return {"state": "DOWNLOADED"}  # type: ignore[return-value]
            if malformed == "string_success":
                return GoogleFlowDownloadEvidence(
                    state="DOWNLOADED",  # type: ignore[arg-type]
                    detail="session-secret=DO_NOT_PERSIST",
                    output_path=destination_path,
                )
            if malformed == "unknown_state":
                return GoogleFlowDownloadEvidence(
                    state="PENDING",  # type: ignore[arg-type]
                    detail="session-secret=DO_NOT_PERSIST",
                )
            if malformed == "null_state":
                return GoogleFlowDownloadEvidence(
                    state=None,  # type: ignore[arg-type]
                    detail="session-secret=DO_NOT_PERSIST",
                )
            if malformed == "numeric_success_path":
                return GoogleFlowDownloadEvidence(
                    state=GoogleFlowDownloadState.DOWNLOADED,
                    detail="session-secret=DO_NOT_PERSIST",
                    output_path=42,  # type: ignore[arg-type]
                )
            return GoogleFlowDownloadEvidence(
                state=GoogleFlowDownloadState.DOWNLOADED,
                detail="session-secret=DO_NOT_PERSIST",
                output_path="",
            )

    driver = MalformedEvidenceDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation") as error:
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert "DO_NOT_PERSIST" not in str(error.value)

    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == "remote:SCENE_001"
    assert stored.output_path is None
    assert "DO_NOT_PERSIST" not in (stored.error_message or "")
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()

    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert not final.exists()
    partials = list(final.parent.glob(final.name + ".*.part"))
    assert len(partials) == int(leave_partial)
    if leave_partial:
        assert partials[0].read_bytes() == b"unknown-browser-result"

    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert len(driver.calls) == 1
    if leave_partial:
        assert partials[0].read_bytes() == b"unknown-browser-result"


@pytest.mark.parametrize(
    "payload",
    [
        b"<html><title>Login required</title></html>",
        b" \n<!DOCTYPE HTML><html>Sign in</html>",
        b"\xef\xbb\xbf\r\n<html>Authentication expired</html>",
        b'{"error":"unauthorized"}',
        b'  [{"message":"generation not ready"}]',
        b'<?xml version="1.0"?><error>Forbidden</error>',
        b"<!-- browser login redirect --><html>Sign in</html>",
        "<html>Sign in to Google</html>".encode("utf-16"),
        b"\xfe\xff" + '{"error":"expired session"}'.encode("utf-16-be"),
        "<?xml version='1.0'?><error>Session expired</error>".encode("utf-16"),
        "<html>Session expired</html>".encode("utf-16-le"),
        "  <html>Login expired</html>".encode("utf-16-be"),
        '{"error":"session expired"}'.encode("utf-32-le"),
        "<!DOCTYPE html><html>Authentication required</html>".encode("utf-32-be"),
        "<html>Session expired</html>".encode("utf-32"),
    ],
)
def test_browser_nonvideo_response_never_becomes_confirmed_mp4(
    tmp_path: Path,
    payload: bytes,
) -> None:
    """An HTML login page or JSON error with an MP4 suffix is not a Download."""

    class NonvideoDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            Path(destination_path).write_bytes(payload)
            return evidence

    driver = NonvideoDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError, match="nonempty regular file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    result = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert result is not None
    assert result.state == DownloadState.ATTENTION_REQUIRED
    assert result.output_path is None
    assert result.generation_remote_result_id == "remote:SCENE_001"

    directory = root / "EP500_DOWNLOAD" / "downloads"
    final = directory / "SCENE_001__take_01.mp4"
    partials = list(directory.glob("SCENE_001__take_01.mp4.*.part"))
    assert not final.exists()
    assert len(partials) == 1
    assert partials[0].read_bytes() == payload
    assert len(driver.calls) == 1
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1


@pytest.mark.parametrize(
    "malformed_suffix",
    [chr(0), chr(0) + "private-token=DO_NOT_PERSIST"],
)
def test_browser_success_path_with_nul_is_ambiguous_and_keeps_partial(
    tmp_path: Path,
    malformed_suffix: str,
) -> None:
    """A malformed success path never bypasses the Download ambiguity contract."""

    class MalformedPathDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            return GoogleFlowDownloadEvidence(
                state=GoogleFlowDownloadState.DOWNLOADED,
                detail="untrusted-browser-result",
                output_path=destination_path + malformed_suffix,
            )

    driver = MalformedPathDriver()
    direct = GoogleFlowDownloadProvider("profile-test", driver)
    standalone = tmp_path / "standalone.mp4"
    request = GeneratedMediaDownloadRequest(
        episode_id="EP500_DOWNLOAD",
        scene_id="SCENE_001",
        remote_result_id="remote:SCENE_001",
        destination_path=str(standalone),
    )
    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation") as raised:
        direct.download(request)
    assert "DO_NOT_PERSIST" not in str(raised.value)
    assert not standalone.exists()
    temporary = list(tmp_path.glob("standalone.mp4.*.part"))
    assert len(temporary) == 1
    assert temporary[0].read_bytes() == b"fake-video"
    assert len(driver.calls) == 1

    root, _jobs, downloads, service = _setup(tmp_path, MalformedPathDriver())
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.ATTENTION_REQUIRED
    assert recorded.generation_remote_result_id == "remote:SCENE_001"
    assert "DO_NOT_PERSIST" not in (recorded.error_message or "")
    assert b"DO_NOT_PERSIST" not in (root / "EP500_DOWNLOAD" / "project.sqlite3").read_bytes()
    folder = root / "EP500_DOWNLOAD" / "downloads"
    preserved = list(folder.glob("SCENE_001__take_01.mp4.*.part"))
    assert len(preserved) == 1
    assert preserved[0].read_bytes() == b"fake-video"
    assert not (folder / "SCENE_001__take_01.mp4").exists()
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")


def test_google_flow_provider_rejects_success_at_wrong_path(tmp_path: Path) -> None:
    class WrongPathDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            del profile_id, remote_result_id, timeout_ms
            wrong = Path(destination_path).with_name("wrong.part")
            wrong.parent.mkdir(parents=True, exist_ok=True)
            wrong.write_bytes(b"wrong")
            return GoogleFlowDownloadEvidence(
                state=GoogleFlowDownloadState.DOWNLOADED,
                detail="wrong path fixture",
                output_path=str(wrong),
            )

    provider = GoogleFlowDownloadProvider("profile-safe", WrongPathDriver())
    request = GeneratedMediaDownloadRequest(
        episode_id="EP500_DOWNLOAD",
        scene_id="SCENE_001",
        remote_result_id="remote:SCENE_001",
        destination_path=str(tmp_path / "final.mp4"),
    )

    with pytest.raises(MediaDownloadAmbiguousError, match="unexpected path"):
        provider.download(request)

    assert not (tmp_path / "final.mp4").exists()


def test_t18_collision_appearing_during_download_never_overwrites_final(tmp_path: Path) -> None:
    class CollisionDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            final = Path(destination_path).parent / "SCENE_001__take_01.mp4"
            final.write_bytes(b"already-owned-final")
            return evidence

    driver = CollisionDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)
    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    with pytest.raises(MediaDownloadAmbiguousError, match="appeared"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert final.read_bytes() == b"already-owned-final"
    partials = list(final.parent.glob(final.name + ".*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"fake-video"
    assert len(driver.calls) == 1
    collision = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert collision is not None
    assert collision.state == DownloadState.ATTENTION_REQUIRED
    assert collision.generation_remote_result_id == "remote:SCENE_001"
    assert collision.output_path is None
    # Even choosing a different take must not silently retry an unresolved
    # collision between two potentially valid MP4 results.
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert len(driver.calls) == 1
    assert not (final.parent / "SCENE_001__take_02.mp4").exists()
    assert final.read_bytes() == b"already-owned-final"
    assert partials[0].read_bytes() == b"fake-video"
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].remote_result_id == "remote:SCENE_001"


@pytest.mark.parametrize("publication_change", ["modified_content", "independent_final"])
def test_published_file_is_rechecked_before_success_and_partial_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    publication_change: str,
) -> None:
    """A late writer or divergent filesystem result must not certify an MP4."""

    from flow_otomatis.workers.browser import google_flow_download

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original_link = google_flow_download.os.link

    def changed_publication(source: str | Path, destination: str | Path) -> None:
        if publication_change == "modified_content":
            original_link(source, destination)
            # Hard links share bytes. A late browser write can invalidate
            # the file after its initial validation but before publication ends.
            Path(destination).write_bytes(b"<!doctype html><html>expired session</html>")
        else:
            # Simulate an unexpected/nonconforming publishing primitive that
            # creates valid-looking but independent bytes at the final path.
            Path(destination).write_bytes(b"independent-file")

    monkeypatch.setattr(google_flow_download.os, "link", changed_publication)
    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    partials = list(final.parent.glob(final.name + ".*.part"))
    assert len(partials) == 1
    assert final.is_file()
    assert partials[0].is_file()
    if publication_change == "modified_content":
        assert final.read_bytes() == b"<!doctype html><html>expired session</html>"
        assert partials[0].read_bytes() == final.read_bytes()
    else:
        assert final.read_bytes() == b"independent-file"
        assert partials[0].read_bytes() == b"fake-video"

    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.ATTENTION_REQUIRED
    assert recorded.output_path is None
    assert recorded.generation_remote_result_id == "remote:SCENE_001"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1


def test_t19_unsupported_no_clobber_primitive_fails_without_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, _downloads, service = _setup(tmp_path, driver)
    from flow_otomatis.workers.browser import google_flow_download

    def forbid_hardlink(*_args, **_kwargs):
        raise OSError("filesystem does not support hard links")

    monkeypatch.setattr(google_flow_download.os, "link", forbid_hardlink)
    with pytest.raises(MediaDownloadAmbiguousError, match="Atomic no-overwrite"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert not final.exists()
    assert len(list(final.parent.glob(final.name + ".*.part"))) == 1
    assert len(driver.calls) == 1


def test_t20_parallel_attempts_publish_once_and_do_not_erase_success(tmp_path: Path) -> None:
    class ConcurrentDriver(FakeDownloadDriver):
        def __init__(self) -> None:
            super().__init__()
            self.barrier = Barrier(2)

        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            self.barrier.wait(timeout=10)
            return evidence

    driver = ConcurrentDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)

    def attempt():
        try:
            return service.download_scene("EP500_DOWNLOAD", "SCENE_001")
        except (MediaDownloadProviderError, InternalInvariantError) as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt)
        second = pool.submit(attempt)
        outcomes = [first.result(timeout=20), second.result(timeout=20)]

    # Both commit orders are safe: the winner may save first (DOWNLOADED),
    # or the losing attempt may save ambiguity first, preventing the winner
    # from overwriting manual-review evidence. Never fabricate a success.
    successes = [item for item in outcomes if isinstance(item, DownloadRecord)]
    errors = [item for item in outcomes if isinstance(item, Exception)]
    assert len(successes) <= 1
    assert len(successes) + len(errors) == 2
    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final.is_file()
    assert final.read_bytes() == b"fake-video"
    assert len(driver.calls) == 2
    assert len({call[2] for call in driver.calls}) == 2
    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    if successes:
        assert len(errors) == 1
        assert recorded.state == DownloadState.DOWNLOADED
        assert recorded.output_path == str(final)
        assert successes[0] == recorded
    else:
        assert len(errors) == 2
        assert recorded.state == DownloadState.ATTENTION_REQUIRED
        assert recorded.output_path is None
        with pytest.raises(InternalInvariantError, match="manual reconciliation"):
            service.download_scene("EP500_DOWNLOAD", "SCENE_001")
        assert len(driver.calls) == 2
    assert final.read_bytes() == b"fake-video"
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].remote_result_id == "remote:SCENE_001"


def test_parallel_losing_attempt_ambiguity_commits_before_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prove that the slower success cannot erase an earlier uncertain result."""

    class ConcurrentDriver(FakeDownloadDriver):
        def __init__(self) -> None:
            super().__init__()
            self.barrier = Barrier(2)

        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            self.barrier.wait(timeout=15)
            return evidence

    driver = ConcurrentDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    ambiguity_committed = Event()
    guarded_save = downloads.save_if_current_generate
    attention_save = downloads.save_attention_if_unconfirmed

    def delay_success_until_ambiguity(record: DownloadRecord, remote_id: str) -> bool:
        assert ambiguity_committed.wait(timeout=15)
        return guarded_save(record, remote_id)

    def record_ambiguity_first(
        record: DownloadRecord, *, expected_remote_result_id: str | None = None
    ) -> None:
        attention_save(record, expected_remote_result_id=expected_remote_result_id)
        ambiguity_committed.set()

    monkeypatch.setattr(downloads, "save_if_current_generate", delay_success_until_ambiguity)
    monkeypatch.setattr(downloads, "save_attention_if_unconfirmed", record_ambiguity_first)

    def attempt() -> DownloadRecord | Exception:
        try:
            return service.download_scene("EP500_DOWNLOAD", "SCENE_001")
        except (MediaDownloadProviderError, InternalInvariantError) as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt)
        second = pool.submit(attempt)
        outcomes = [first.result(timeout=25), second.result(timeout=25)]

    assert len(driver.calls) == 2
    assert ambiguity_committed.is_set()
    assert sum(isinstance(item, MediaDownloadAmbiguousError) for item in outcomes) == 1
    assert sum(isinstance(item, InternalInvariantError) for item in outcomes) == 1
    assert not any(isinstance(item, DownloadRecord) for item in outcomes)
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None and record.state == DownloadState.ATTENTION_REQUIRED
    assert record.output_path is None

    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final.read_bytes() == b"fake-video"
    partials = list(final.parent.glob(final.name + ".*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"fake-video"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 2


def test_t21_file_publish_success_db_failure_requires_manual_reconciliation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = FakeDownloadDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)
    real_save = downloads.save_if_current_generate

    def interrupted_persistence(record, remote_result_id):
        if record.state == DownloadState.DOWNLOADED:
            raise StorageError("synthetic commit failure")
        return real_save(record, remote_result_id)

    monkeypatch.setattr(downloads, "save_if_current_generate", interrupted_persistence)
    with pytest.raises(StorageError, match="synthetic"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final.is_file()
    assert final.read_bytes() == b"fake-video"
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].remote_result_id == "remote:SCENE_001"


def test_conditional_failure_cannot_replace_historical_downloaded_record(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    failed = __import__("dataclasses").replace(
        original, state=DownloadState.FAILED, output_path=None, error_message="rival failed"
    )
    downloads.save_failure_if_unconfirmed(failed)
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original


def test_download_worker_never_publishes_a_linked_partial_even_if_driver_claims_success(
    tmp_path: Path,
) -> None:
    class LinkedPartialDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            del profile_id, remote_result_id, timeout_ms
            destination = Path(destination_path)
            outside = tmp_path / "unrelated.mp4"
            outside.write_bytes(b"not-a-provider-download")
            try:
                destination.symlink_to(outside)
            except OSError, NotImplementedError:
                pytest.skip("This Windows runner cannot create symbolic links")
            return GoogleFlowDownloadEvidence(
                state=GoogleFlowDownloadState.DOWNLOADED,
                detail="synthetic malicious success",
                output_path=str(destination),
            )

    _root, _jobs, downloads, service = _setup(tmp_path, LinkedPartialDriver())
    with pytest.raises(MediaDownloadAmbiguousError, match="nonempty regular file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    failure = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert failure is not None and failure.state == DownloadState.ATTENTION_REQUIRED
    assert failure.output_path is None
    assert not list((tmp_path / "projects").rglob("SCENE_001__take_01.mp4"))


@pytest.mark.parametrize(
    "variant",
    ["wrong_path", "wrong_path_with_final", "missing_file", "empty_final"],
)
def test_unverified_provider_success_requires_review_and_preserves_outputs(
    tmp_path: Path,
    variant: str,
) -> None:
    """A typed success cannot permit a retry if the MP4 evidence is unverified."""

    class UnverifiedProvider:
        def __init__(self) -> None:
            self.calls = 0

        def download(self, request: GeneratedMediaDownloadRequest) -> GeneratedMediaDownloadResult:
            self.calls += 1
            final = Path(request.destination_path)
            final.parent.mkdir(parents=True, exist_ok=True)
            if variant.startswith("wrong_path"):
                alternate = tmp_path / "outside.mp4"
                alternate.write_bytes(b"unrelated-output")
                if variant == "wrong_path_with_final":
                    final.write_bytes(b"uncertain-canonical")
                return GeneratedMediaDownloadResult(output_path=str(alternate))
            if variant == "empty_final":
                final.write_bytes(b"")
            return GeneratedMediaDownloadResult(output_path=str(final))

    provider = UnverifiedProvider()
    root, _jobs, downloads, service = _setup(tmp_path, FakeDownloadDriver())
    service._provider = provider  # type: ignore[assignment]

    with pytest.raises(MediaDownloadAmbiguousError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == "remote:SCENE_001"
    assert stored.take == 1
    assert stored.output_path is None
    assert stored.error_message is not None

    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    if variant == "wrong_path_with_final":
        assert final.read_bytes() == b"uncertain-canonical"
    elif variant == "empty_final":
        assert final.is_file() and final.stat().st_size == 0
    else:
        assert not final.exists()
    if variant.startswith("wrong_path"):
        assert (tmp_path / "outside.mp4").read_bytes() == b"unrelated-output"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert provider.calls == 1
    if variant == "wrong_path_with_final":
        assert final.read_bytes() == b"uncertain-canonical"


def test_download_service_rejects_provider_symlink_success_with_sticky_review(
    tmp_path: Path,
) -> None:
    from flow_otomatis.application.ports.generated_media_download import (
        GeneratedMediaDownloadResult,
    )

    class LinkedFinalProvider:
        def download(self, request: GeneratedMediaDownloadRequest) -> GeneratedMediaDownloadResult:
            dst = Path(request.destination_path)
            target = tmp_path / "unrelated-existing-file.mp4"
            target.write_bytes(b"unrelated-bytes")
            try:
                dst.symlink_to(target)
            except OSError, NotImplementedError:
                pytest.skip("This Windows runner cannot create symbolic links")
            return GeneratedMediaDownloadResult(output_path=str(dst))

    _root, jobs, downloads, original = _setup(tmp_path, FakeDownloadDriver())
    service = GeneratedMediaDownloadService(
        jobs, downloads, LinkedFinalProvider(), tmp_path / "projects"
    )
    with pytest.raises(MediaDownloadAmbiguousError, match="unavailable or redirected MP4"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    stored = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert stored is not None
    assert stored.state == DownloadState.ATTENTION_REQUIRED
    assert stored.generation_remote_result_id == "remote:SCENE_001"
    assert stored.output_path is None
    symlink = tmp_path / "projects" / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert symlink.is_symlink()
    assert symlink.read_bytes() == b"unrelated-bytes"
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)
    assert symlink.is_symlink()


def test_download_worker_rejects_invalid_partial_even_when_symlink_creation_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Test the explicit guard even on locked-down Windows hosts where creating
    # a real symbolic link requires elevated privileges.
    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    original_check = Path.is_symlink

    def simulated_link(self: Path) -> bool:
        if self.suffix == ".part":
            return True
        return original_check(self)

    monkeypatch.setattr(Path, "is_symlink", simulated_link)
    with pytest.raises(MediaDownloadAmbiguousError, match="nonempty regular file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    failure = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert failure is not None and failure.state == DownloadState.ATTENTION_REQUIRED
    assert failure.output_path is None


def test_service_refuses_redirected_project_download_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A downloaded MP4 must not escape the configured project root."""

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    directory = root / "EP500_DOWNLOAD" / "downloads"
    original_is_junction = Path.is_junction

    def simulated_junction(self: Path) -> bool:
        return self == directory or original_is_junction(self)

    # Deterministic on Windows runners without symlink creation privileges.
    monkeypatch.setattr(Path, "is_junction", simulated_junction)
    with pytest.raises(InternalInvariantError, match="redirected"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert not directory.exists()
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert driver.calls == []


def test_service_refuses_real_symlinked_download_folder(
    tmp_path: Path,
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    outside = tmp_path / "unrelated-output"
    outside.mkdir()
    redirected = root / "EP500_DOWNLOAD" / "downloads"
    try:
        redirected.symlink_to(outside, target_is_directory=True)
    except OSError, NotImplementedError:
        pytest.skip("Runner cannot create a directory symbolic link")

    with pytest.raises(InternalInvariantError, match="redirected"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert list(outside.iterdir()) == []
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert driver.calls == []


def test_download_worker_direct_call_blocks_redirected_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A direct worker caller cannot bypass the main service's path gate."""

    driver = FakeDownloadDriver()
    worker = GoogleFlowDownloadProvider("profile-safe", driver)
    target = tmp_path / "downloads" / "SCENE_001__take_01.mp4"
    original_is_symlink = Path.is_symlink

    def redirected(self: Path) -> bool:
        return self == target.parent or original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", redirected)
    request = GeneratedMediaDownloadRequest(
        episode_id="EP500_DOWNLOAD",
        scene_id="SCENE_001",
        remote_result_id="remote:SCENE_001",
        destination_path=str(target),
    )
    with pytest.raises(MediaDownloadProviderError, match="folder is redirected"):
        worker.download(request)
    assert driver.calls == []
    assert not target.exists()


def test_download_worker_rejects_parent_redirected_during_async_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Late junction swap leaves the private .part, never publishes MP4."""

    driver = FakeDownloadDriver()
    worker = GoogleFlowDownloadProvider("profile-safe", driver)
    target = tmp_path / "downloads" / "SCENE_001__take_01.mp4"
    checks = 0
    original_is_junction = Path.is_junction

    def redirected_after_driver(self: Path) -> bool:
        nonlocal checks
        if self == target.parent:
            checks += 1
            return checks >= 2
        return original_is_junction(self)

    monkeypatch.setattr(Path, "is_junction", redirected_after_driver)
    request = GeneratedMediaDownloadRequest(
        episode_id="EP500_DOWNLOAD",
        scene_id="SCENE_001",
        remote_result_id="remote:SCENE_001",
        destination_path=str(target),
    )
    with pytest.raises(MediaDownloadAmbiguousError, match="changed during the attempt"):
        worker.download(request)
    assert len(driver.calls) == 1
    assert not target.exists()
    partials = list(target.parent.glob("*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"fake-video"


def test_existing_download_must_match_requested_take_before_idempotent_reuse(
    tmp_path: Path,
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    first = service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=1)
    second = service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)

    assert first.take == 1
    assert second.take == 2
    assert first.output_path != second.output_path
    assert second.output_path is not None
    assert second.output_path.endswith("SCENE_001__take_02.mp4")
    assert Path(first.output_path or "").read_bytes() == b"fake-video"
    assert Path(second.output_path).read_bytes() == b"fake-video"
    assert Path(second.output_path).is_relative_to(root)
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == second
    assert len(driver.calls) == 2
    assert service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2) == second
    assert len(driver.calls) == 2


def test_existing_success_does_not_bypass_redirected_download_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    success = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    directory = root / "EP500_DOWNLOAD" / "downloads"
    before_calls = len(driver.calls)
    original_junction = Path.is_junction

    def redirect_after_success(self: Path) -> bool:
        return self == directory or original_junction(self)

    monkeypatch.setattr(Path, "is_junction", redirect_after_success)
    with pytest.raises(InternalInvariantError, match="redirected"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == success
    assert len(driver.calls) == before_calls


@pytest.mark.parametrize(
    ("new_state", "remote_result_id", "expected_error"),
    [
        (GenerationJobState.FAILED, "remote:SCENE_001", "GENERATED"),
        (GenerationJobState.QUEUED, "remote:SCENE_001", "GENERATED"),
        (GenerationJobState.GENERATED, None, "remote result identifier"),
    ],
)
def test_confirmed_mp4_reuse_requires_current_generated_job(
    tmp_path: Path,
    new_state: GenerationJobState,
    remote_result_id: str | None,
    expected_error: str,
) -> None:
    """Historical MP4 files cannot bypass a later Generate invalidation."""

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    completed = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert completed.state == DownloadState.DOWNLOADED
    assert len(driver.calls) == 1
    assert Path(completed.output_path or "").read_bytes() == b"fake-video"

    with __import__("sqlite3").connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as connection:
        connection.execute(
            """
            UPDATE generation_jobs SET state = ?, remote_result_id = ?
            WHERE job_id = ?
            """,
            (
                new_state.value,
                remote_result_id,
                "EP500_DOWNLOAD:SCENE_001:GENERATE",
            ),
        )
        connection.commit()

    with pytest.raises(InternalInvariantError, match=expected_error):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    # Fail closed, but never erase a previously confirmed local file or row.
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == completed
    assert Path(completed.output_path or "").read_bytes() == b"fake-video"
    assert len(driver.calls) == 1


@pytest.mark.parametrize(
    ("episode_id", "scene_id"),
    [
        ("EP500_DOWNLOAD:alternate", "SCENE_001"),
        ("EP500_DOWNLOAD.", "SCENE_001"),
        ("EP500_DOWNLOAD ", "SCENE_001"),
        ("CON", "SCENE_001"),
        ("PRN.txt", "SCENE_001"),
        ("LPT9", "SCENE_001"),
        ("EP500_DOWNLOAD", "SCENE_001:other"),
        ("EP500_DOWNLOAD", "SCENE_001?"),
        ("EP500_DOWNLOAD", "SCENE_001."),
        ("EP500_DOWNLOAD", "AUX.mp4"),
        ("EP500_DOWNLOAD", "SCENE_001\\evil"),
        ("EP500_DOWNLOAD", "SCENE_001\x00bad"),
    ],
)
def test_download_blocks_unsafe_windows_components_before_any_provider_or_write(
    tmp_path: Path, episode_id: str, scene_id: str
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)

    with pytest.raises(InternalInvariantError, match="Unsafe"):
        service.download_scene(episode_id, scene_id)

    assert driver.calls == []
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert not (root / "CON").exists()
    assert not (root / "EP500_DOWNLOAD" / "downloads").exists()


@pytest.mark.parametrize(
    ("late_state", "late_remote_id"),
    [
        (GenerationJobState.QUEUED, None),
        (GenerationJobState.FAILED, "remote:SCENE_001"),
        (GenerationJobState.GENERATED, "remote:replacement"),
        (GenerationJobState.GENERATED, ""),
    ],
)
def test_download_worker_result_is_not_saved_if_generate_changed_midflight(
    tmp_path: Path, late_state: GenerationJobState, late_remote_id: str | None
) -> None:
    database = tmp_path / "projects" / "EP500_DOWNLOAD" / "project.sqlite3"

    class MidflightJobChangeDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            evidence = super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )
            # A concurrent generation worker invalidates the original result
            # after the download wrote bytes but before the service persists.
            with __import__("sqlite3").connect(database) as connection:
                connection.execute(
                    "UPDATE generation_jobs SET state = ?, remote_result_id = ? WHERE scene_id = ?",
                    (late_state.value, late_remote_id, "SCENE_001"),
                )
                connection.commit()
            return evidence

    driver = MidflightJobChangeDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)
    published = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    with pytest.raises(InternalInvariantError, match="changed during Download"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert len(driver.calls) == 1
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert published.read_bytes() == b"fake-video"
    job = jobs.list_for_episode("EP500_DOWNLOAD")[0]
    assert job.state is late_state
    assert job.remote_result_id == late_remote_id


@pytest.mark.parametrize(
    ("new_state", "new_remote_id"),
    [
        (GenerationJobState.QUEUED, None),
        (GenerationJobState.FAILED, None),
        (GenerationJobState.ATTENTION_REQUIRED, None),
        (GenerationJobState.GENERATED, "remote:changed"),
    ],
)
def test_atomic_download_commit_rejects_state_change_after_last_service_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    new_state: GenerationJobState,
    new_remote_id: str | None,
) -> None:
    """Reject a Generate change made immediately before the atomic write."""

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    save_guarded = downloads.save_if_current_generate
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"

    def stale_before_commit(record, remote_result_id):
        with __import__("sqlite3").connect(database) as connection:
            connection.execute(
                "UPDATE generation_jobs SET state = ?, remote_result_id = ? WHERE scene_id = ?",
                (new_state.value, new_remote_id, record.scene_id),
            )
            connection.commit()
        return save_guarded(record, remote_result_id)

    monkeypatch.setattr(downloads, "save_if_current_generate", stale_before_commit)

    with pytest.raises(InternalInvariantError, match="atomic Download save"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    output = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert output.read_bytes() == b"fake-video"
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None
    assert len(driver.calls) == 1


def test_atomic_download_commit_allows_matching_generated_result(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    record = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == record
    assert record.state == DownloadState.DOWNLOADED


def test_atomic_download_commit_rejects_stale_replacement_without_erasing_history(
    tmp_path: Path,
) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    video = Path(original.output_path or "")
    assert video.read_bytes() == b"fake-video"

    with __import__("sqlite3").connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as connection:
        connection.execute(
            "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
            ("remote:NEW_RESULT", "SCENE_001"),
        )
        connection.commit()

    from dataclasses import replace

    rival = replace(
        original,
        output_path=str(video.with_name("rival.mp4")),
        updated_at=datetime.now(UTC),
    )
    assert downloads.save_if_current_generate(rival, "remote:SCENE_001") is False
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    assert video.read_bytes() == b"fake-video"


def test_atomic_download_commit_disallows_non_success_or_blank_expected_result(
    tmp_path: Path,
) -> None:
    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    confirmed = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    from dataclasses import replace

    with pytest.raises(ValueError, match="Only DOWNLOADED"):
        downloads.save_if_current_generate(
            replace(confirmed, state=DownloadState.FAILED), "remote:SCENE_001"
        )
    with pytest.raises(ValueError, match="must not be blank"):
        downloads.save_if_current_generate(confirmed, "  ")
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == confirmed


def test_download_does_not_reuse_mp4_from_another_generated_result(tmp_path: Path) -> None:
    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    video = Path(original.output_path or "")
    assert original.generation_remote_result_id == "remote:SCENE_001"

    with __import__("sqlite3").connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as db:
        db.execute(
            "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
            ("remote:NEW_GENERATED", "SCENE_001"),
        )
        db.commit()
    with pytest.raises(InternalInvariantError, match="will not be overwritten"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    assert video.read_bytes() == b"fake-video"
    assert len(driver.calls) == 1


def test_new_generated_identity_cannot_replace_confirmed_download_history(
    tmp_path: Path,
) -> None:
    """A new valid Generate result cannot erase an older successful Download row."""

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    previous = service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=1)
    previous_video = Path(previous.output_path or "")
    assert previous.generation_remote_result_id == "remote:SCENE_001"

    with __import__("sqlite3").connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as db:
        db.execute(
            "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
            ("remote:NEW_GENERATED", "SCENE_001"),
        )
        db.commit()

    # A different take has a free destination. Without a transaction-level
    # conflict guard it could replace the old SQLite row despite being a
    # distinct Generate identity.
    with pytest.raises(InternalInvariantError, match="atomic Download save"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001", take=2)

    newer_video = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_02.mp4"
    assert newer_video.read_bytes() == b"fake-video"
    assert previous_video.read_bytes() == b"fake-video"
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == previous
    assert len(driver.calls) == 2


def test_sticky_ambiguous_record_survives_late_failure_and_success_commit(
    tmp_path: Path,
) -> None:
    """An unresolved provider attempt cannot be silently cleared by a rival."""

    driver = FakeDownloadDriver(GoogleFlowDownloadState.AMBIGUOUS)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    old = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert old is not None
    assert old.state == DownloadState.ATTENTION_REQUIRED

    from dataclasses import replace

    failed = replace(old, state=DownloadState.FAILED, error_message="late failure")
    downloads.save_failure_if_unconfirmed(failed)
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == old

    confirmed = replace(
        old,
        state=DownloadState.DOWNLOADED,
        output_path=str(root / "EP500_DOWNLOAD" / "downloads" / "fake.mp4"),
        error_message=None,
    )
    assert downloads.save_if_current_generate(confirmed, "remote:SCENE_001") is False
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == old


def test_ambiguous_attempt_does_not_erase_prior_confirmed_result(tmp_path: Path) -> None:
    """A late uncertain rival leaves the original MP4 and history untouched."""

    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    video = Path(original.output_path or "")
    assert video.read_bytes() == b"fake-video"

    from dataclasses import replace

    ambiguous = replace(
        original,
        state=DownloadState.ATTENTION_REQUIRED,
        output_path=None,
        error_message="rival timed out",
    )
    downloads.save_attention_if_unconfirmed(ambiguous)
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    assert video.read_bytes() == b"fake-video"


def test_operator_review_releases_ambiguous_download_with_audit_without_retry(
    tmp_path: Path,
) -> None:
    """Review authorizes a *future* user-initiated attempt, not a hidden retry."""

    import sqlite3

    class PartialAmbiguousDriver(FakeDownloadDriver):
        def download_one(
            self,
            profile_id: str,
            remote_result_id: str,
            destination_path: str,
            *,
            timeout_ms: int,
        ) -> GoogleFlowDownloadEvidence:
            if self.state is GoogleFlowDownloadState.AMBIGUOUS:
                path = Path(destination_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"uncertain-original-partial")
            return super().download_one(
                profile_id, remote_result_id, destination_path, timeout_ms=timeout_ms
            )

    driver = PartialAmbiguousDriver(GoogleFlowDownloadState.AMBIGUOUS)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    ambiguous = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert ambiguous is not None
    assert ambiguous.state == DownloadState.ATTENTION_REQUIRED
    partials = list((root / "EP500_DOWNLOAD" / "downloads").glob("*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"uncertain-original-partial"

    args = {
        "expected_remote_result_id": "remote:SCENE_001",
        "expected_updated_at": ambiguous.updated_at.isoformat(),
    }
    with pytest.raises(InternalInvariantError, match="Manual provider"):
        service.release_retry_after_manual_review(
            "EP500_DOWNLOAD", "SCENE_001", reviewed_provider_and_local_files=False, **args
        )
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == ambiguous
    assert len(driver.calls) == 1

    released = service.release_retry_after_manual_review(
        "EP500_DOWNLOAD", "SCENE_001", reviewed_provider_and_local_files=True, **args
    )
    assert released.state == DownloadState.FAILED
    assert released.generation_remote_result_id == "remote:SCENE_001"
    assert released.output_path is None
    assert partials[0].read_bytes() == b"uncertain-original-partial"
    assert len(driver.calls) == 1  # clearing the gate never calls the provider

    database = root / "EP500_DOWNLOAD" / "project.sqlite3"
    with sqlite3.connect(database) as conn:
        audit = conn.execute(
            """SELECT generation_remote_result_id, prior_updated_at,
                      action, prior_error_message
               FROM download_reconciliation_audit"""
        ).fetchall()
    assert len(audit) == 1
    assert audit[0][0] == "remote:SCENE_001"
    assert audit[0][1] == args["expected_updated_at"]
    assert audit[0][2] == "OPERATOR_REVIEWED_RETRY"
    assert audit[0][3] is not None

    # The old reviewer revision is no longer valid and cannot release again.
    with pytest.raises(InternalInvariantError, match="evidence changed"):
        service.release_retry_after_manual_review(
            "EP500_DOWNLOAD", "SCENE_001", reviewed_provider_and_local_files=True, **args
        )
    driver.state = GoogleFlowDownloadState.DOWNLOADED
    confirmed = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert confirmed.state == DownloadState.DOWNLOADED
    assert len(driver.calls) == 2
    assert partials[0].read_bytes() == b"uncertain-original-partial"
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM download_reconciliation_audit").fetchone()[0] == 1


def test_reconciliation_accepts_current_generate_with_historical_whitespace(
    tmp_path: Path,
) -> None:
    """Use the same normalized remote ID as Download's guarded persistence."""

    import sqlite3

    driver = FakeDownloadDriver(GoogleFlowDownloadState.AMBIGUOUS)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"

    # Generation rows may have legacy whitespace even though the download
    # boundary normalizes the ID before storing the ambiguity.
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
            ("  remote:SCENE_001  ", "SCENE_001"),
        )
        connection.commit()

    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    ambiguous = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert ambiguous is not None
    assert ambiguous.state == DownloadState.ATTENTION_REQUIRED
    assert ambiguous.generation_remote_result_id == "remote:SCENE_001"

    released = service.release_retry_after_manual_review(
        "EP500_DOWNLOAD",
        "SCENE_001",
        expected_remote_result_id="remote:SCENE_001",
        expected_updated_at=ambiguous.updated_at.isoformat(),
        reviewed_provider_and_local_files=True,
    )
    assert released.state == DownloadState.FAILED
    assert released.output_path is None
    assert len(driver.calls) == 1
    with sqlite3.connect(database) as connection:
        assert (
            connection.execute(
                "SELECT remote_result_id FROM generation_jobs WHERE scene_id = ?",
                ("SCENE_001",),
            ).fetchone()[0]
            == "  remote:SCENE_001  "
        )
        assert (
            connection.execute("SELECT COUNT(*) FROM download_reconciliation_audit").fetchone()[0]
            == 1
        )


def test_ambiguous_reconciliation_rejects_stale_generate_and_download_revisions(
    tmp_path: Path,
) -> None:
    import sqlite3

    driver = FakeDownloadDriver(GoogleFlowDownloadState.AMBIGUOUS)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    original = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert original is not None
    database = root / "EP500_DOWNLOAD" / "project.sqlite3"
    expected_time = original.updated_at.isoformat()
    base = {
        "expected_remote_result_id": "remote:SCENE_001",
        "reviewed_provider_and_local_files": True,
    }
    with pytest.raises(InternalInvariantError, match="evidence changed"):
        service.release_retry_after_manual_review(
            "EP500_DOWNLOAD", "SCENE_001", expected_updated_at="2020-01-01T00:00:00+00:00", **base
        )
    with sqlite3.connect(database) as conn:
        conn.execute(
            "UPDATE generation_jobs SET remote_result_id = ? WHERE scene_id = ?",
            ("remote:replacement", "SCENE_001"),
        )
        conn.commit()

    with pytest.raises(InternalInvariantError, match="retry is not authorized"):
        service.release_retry_after_manual_review(
            "EP500_DOWNLOAD", "SCENE_001", expected_updated_at=expected_time, **base
        )
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    with sqlite3.connect(database) as conn:
        assert (
            conn.execute(
                "SELECT name FROM sqlite_master WHERE name = 'download_reconciliation_audit'"
            ).fetchone()
            is None
        )
    assert len(driver.calls) == 1


def test_manual_review_refuses_existing_canonical_mp4_and_keeps_ambiguous_history(
    tmp_path: Path,
) -> None:
    import sqlite3

    driver = FakeDownloadDriver(GoogleFlowDownloadState.AMBIGUOUS)
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    previous = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert previous is not None
    video = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    video.write_bytes(b"possible-existing-download")
    with pytest.raises(InternalInvariantError, match="destination exists"):
        service.release_retry_after_manual_review(
            "EP500_DOWNLOAD",
            "SCENE_001",
            expected_remote_result_id="remote:SCENE_001",
            expected_updated_at=previous.updated_at.isoformat(),
            reviewed_provider_and_local_files=True,
        )
    assert video.read_bytes() == b"possible-existing-download"
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == previous
    with sqlite3.connect(root / "EP500_DOWNLOAD" / "project.sqlite3") as conn:
        assert (
            conn.execute(
                "SELECT name FROM sqlite_master WHERE name = 'download_reconciliation_audit'"
            ).fetchone()
            is None
        )


@pytest.mark.parametrize(
    "replacement_state",
    [DownloadState.FAILED, DownloadState.ATTENTION_REQUIRED, DownloadState.DOWNLOADED],
)
def test_plain_save_cannot_downgrade_or_repoint_confirmed_mp4(
    tmp_path: Path,
    replacement_state: str,
) -> None:
    """The legacy convenience upsert cannot erase immutable success evidence."""

    from dataclasses import replace

    driver = FakeDownloadDriver()
    root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    path = Path(original.output_path or "")
    original_bytes = path.read_bytes()

    alternate = replace(
        original,
        state=replacement_state,
        updated_at=datetime.now(UTC),
        output_path=str(path.with_name("different-take.mp4")),
        take=2,
        error_message="unsafe replacement",
    )
    downloads.save(alternate)
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    assert path.read_bytes() == original_bytes
    assert not path.with_name("different-take.mp4").exists()
    assert len(driver.calls) == 1
    assert (root / "EP500_DOWNLOAD" / "project.sqlite3").exists()


@pytest.mark.parametrize(
    "replacement_state",
    [DownloadState.FAILED, DownloadState.ATTENTION_REQUIRED, DownloadState.DOWNLOADED],
)
def test_plain_save_does_not_clear_unreviewed_ambiguity(
    tmp_path: Path,
    replacement_state: str,
) -> None:
    """Only audited manual reconciliation can release ATTENTION_REQUIRED."""

    from dataclasses import replace

    driver = FakeDownloadDriver(GoogleFlowDownloadState.AMBIGUOUS)
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    with pytest.raises(MediaDownloadAmbiguousError):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    original = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert original is not None
    assert original.state == DownloadState.ATTENTION_REQUIRED

    downloads.save(
        replace(
            original,
            state=replacement_state,
            updated_at=datetime.now(UTC),
            output_path="/unsafe/stale.mp4",
            error_message="attempt to erase ambiguity",
        )
    )
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    with pytest.raises(InternalInvariantError, match="manual reconciliation"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert len(driver.calls) == 1


@pytest.mark.parametrize("variation", ["different_mp4", "different_take", "different_remote"])
def test_guarded_success_rejects_same_generate_id_but_changed_confirmed_identity(
    tmp_path: Path,
    variation: str,
) -> None:
    """The exact remote ID alone cannot authorize replacing recorded MP4 evidence."""

    from dataclasses import replace

    driver = FakeDownloadDriver()
    _root, _jobs, downloads, service = _setup(tmp_path, driver)
    original = service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    changed = {"updated_at": datetime.now(UTC)}
    if variation == "different_mp4":
        changed["output_path"] = str(Path(original.output_path or "").with_name("other.mp4"))
    elif variation == "different_take":
        changed["take"] = 3
    else:
        changed["generation_remote_result_id"] = "remote:DIFFERENT"
    attempted = replace(original, **changed)
    if variation == "different_remote":
        with pytest.raises(ValueError, match="identity does not match"):
            downloads.save_if_current_generate(attempted, "remote:SCENE_001")
    else:
        assert downloads.save_if_current_generate(attempted, "remote:SCENE_001") is False
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") == original
    assert Path(original.output_path or "").read_bytes() == b"fake-video"
    assert len(driver.calls) == 1
