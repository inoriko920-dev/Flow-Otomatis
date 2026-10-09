from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier

import pytest

from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadRequest,
    MediaDownloadAmbiguousError,
    MediaDownloadAuthenticationRequiredError,
    MediaDownloadProviderError,
)
from flow_otomatis.application.services.generated_media_download import (
    GeneratedMediaDownloadService,
)
from flow_otomatis.domain.errors import InternalInvariantError, StorageError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.result import DownloadState
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
        scenes=(),
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
    ("state", "error_type"),
    [
        (
            GoogleFlowDownloadState.AUTH_REQUIRED,
            MediaDownloadAuthenticationRequiredError,
        ),
        (GoogleFlowDownloadState.AMBIGUOUS, MediaDownloadAmbiguousError),
    ],
)
def test_controlled_download_failure_records_failure_without_retry(
    tmp_path: Path,
    state: GoogleFlowDownloadState,
    error_type: type[Exception],
) -> None:
    driver = FakeDownloadDriver(state)
    _root, _jobs, downloads, service = _setup(tmp_path, driver)

    with pytest.raises(error_type):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")

    assert len(driver.calls) == 1
    record = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert record is not None
    assert record.state == DownloadState.FAILED
    assert record.output_path is None


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
    with pytest.raises(MediaDownloadProviderError, match="appeared"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert final.read_bytes() == b"already-owned-final"
    partials = list(final.parent.glob(final.name + ".*.part"))
    assert len(partials) == 1
    assert partials[0].read_bytes() == b"fake-video"
    assert len(driver.calls) == 1
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001").state == DownloadState.FAILED
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].remote_result_id == "remote:SCENE_001"


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
        except MediaDownloadProviderError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt)
        second = pool.submit(attempt)
        outcomes = [first.result(timeout=20), second.result(timeout=20)]

    assert sum(isinstance(item, Exception) for item in outcomes) == 1
    assert sum(getattr(item, "state", None) == DownloadState.DOWNLOADED for item in outcomes) == 1
    final = root / "EP500_DOWNLOAD" / "downloads" / "SCENE_001__take_01.mp4"
    assert final.is_file()
    assert final.read_bytes() == b"fake-video"
    assert len(driver.calls) == 2
    assert len({call[2] for call in driver.calls}) == 2
    recorded = downloads.get("EP500_DOWNLOAD", "SCENE_001")
    assert recorded is not None
    assert recorded.state == DownloadState.DOWNLOADED
    assert recorded.output_path == str(final)
    assert jobs.list_for_episode("EP500_DOWNLOAD")[0].remote_result_id == "remote:SCENE_001"


def test_t21_file_publish_success_db_failure_requires_manual_reconciliation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = FakeDownloadDriver()
    root, jobs, downloads, service = _setup(tmp_path, driver)
    real_save = downloads.save

    def interrupted_persistence(record):
        if record.state == DownloadState.DOWNLOADED:
            raise StorageError("synthetic commit failure")
        return real_save(record)

    monkeypatch.setattr(downloads, "save", interrupted_persistence)
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
    assert failure is not None and failure.state == DownloadState.FAILED
    assert failure.output_path is None
    assert not list((tmp_path / "projects").rglob("SCENE_001__take_01.mp4"))


def test_download_service_rejects_provider_symlink_success_without_persisting(
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
    with pytest.raises(InternalInvariantError, match="regular file"):
        service.download_scene("EP500_DOWNLOAD", "SCENE_001")
    assert downloads.get("EP500_DOWNLOAD", "SCENE_001") is None


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
    assert failure is not None and failure.state == DownloadState.FAILED
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
