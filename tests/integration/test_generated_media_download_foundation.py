from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadRequest,
    MediaDownloadAmbiguousError,
    MediaDownloadAuthenticationRequiredError,
)
from flow_otomatis.application.services.generated_media_download import (
    GeneratedMediaDownloadService,
)
from flow_otomatis.domain.errors import InternalInvariantError
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
    with __import__("sqlite3").connect(projects_root / "EP500_DOWNLOAD" / "project.sqlite3") as connection:
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
    destination = (
        tmp_path
        / "projects"
        / "EP500_DOWNLOAD"
        / "downloads"
        / "SCENE_001__take_01.mp4"
    )
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
