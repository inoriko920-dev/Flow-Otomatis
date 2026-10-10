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
