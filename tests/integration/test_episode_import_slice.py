from __future__ import annotations

import json
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.application.services import EpisodeImportService
from flow_otomatis.domain.errors import (
    PackageSecurityError,
    PackageValidationError,
    WorkspaceAlreadyExistsError,
)
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.result import DownloadRecord, DownloadState
from flow_otomatis.domain.scene import SceneReadiness
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)


def _manifest(*, first_target: float = 7.32) -> dict[str, object]:
    scenes: list[dict[str, object]] = [
        {
            "scene_id": "SCENE_016",
            "target_duration_s": first_target,
            "recommended_flow_duration_s": 10,
            "selected_flow_duration_s": None,
            "image_file": "../08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
            "motion_prompt": "Slow cinematic push-in with stable identity.",
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "status": "READY_FOR_DURATION_SELECTION",
            "trim_target_s": first_target,
        },
        {
            "scene_id": "SCENE_017",
            "target_duration_s": 5.42,
            "recommended_flow_duration_s": 6,
            "selected_flow_duration_s": 6,
            "image_file": "../08_APPROVED_IMAGES/EP001__IMAGE__SCENE_017__v1.0.png",
            "motion_prompt": "Subtle parallax and a controlled camera move.",
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "status": "READY",
            "trim_target_s": 5.42,
        },
    ]
    return {
        "schema_version": "1.0",
        "episode_id": "EP001_STEVE_JOBS",
        "project_name": "Steve Jobs Animated Biography",
        "production_profile": {
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
        },
        "scene_count": len(scenes),
        "scenes": scenes,
        "created_at": "2026-10-07T01:00:00+07:00",
        "source_versions": {
            "audio": "v1.0",
            "srt": "v1.0",
            "beat_map": "v1.0",
            "storyboard": "v1.0",
            "images": "v1.0",
        },
    }


def _write_package(path: Path, manifest: dict[str, object]) -> Path:
    root = "EP001_STEVE_JOBS_COMPLETE"
    manifest_name = f"{root}/09_FLOW_PROMPTS_AND_TAKES/FLOW_OTOMATIS_IMPORT.json"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(manifest_name, json.dumps(manifest))
        archive.writestr(
            f"{root}/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
            b"synthetic-image-16",
        )
        archive.writestr(
            f"{root}/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_017__v1.0.png",
            b"synthetic-image-17",
        )
    return path


def test_happy_path_validates_recomputes_and_persists_workspace(tmp_path: Path) -> None:
    package = _write_package(tmp_path / "episode.zip", _manifest())
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    service = EpisodeImportService(EpisodePackageReader(), repository)

    draft = service.validate(package)

    assert draft.episode_id == "EP001_STEVE_JOBS"
    assert len(draft.scenes) == 2
    assert draft.scenes[0].recommended_flow_duration_s == 8
    assert draft.scenes[0].readiness is SceneReadiness.NEEDS_DURATION_SELECTION
    assert draft.scenes[1].readiness is SceneReadiness.READY
    assert draft.blocking_count == 0

    persisted = service.create_workspace(draft)
    reloaded = repository.load("EP001_STEVE_JOBS")

    assert persisted == reloaded
    assert reloaded is not None
    assert reloaded.scenes[0].target_duration_s == 7.32
    assert (tmp_path / "projects" / "EP001_STEVE_JOBS" / "project.sqlite3").is_file()


def test_target_over_ten_seconds_is_rejected_before_persistence(tmp_path: Path) -> None:
    package = _write_package(
        tmp_path / "invalid-duration.zip",
        _manifest(first_target=10.01),
    )
    projects_root = tmp_path / "projects"
    service = EpisodeImportService(
        EpisodePackageReader(),
        SqliteWorkspaceRepository(projects_root),
    )

    with pytest.raises(PackageValidationError) as exc_info:
        service.import_package(package)

    assert exc_info.value.code == "MANIFEST_SCHEMA_INVALID"
    assert not projects_root.exists()


def test_zip_path_traversal_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../outside.txt", "unsafe")
        archive.writestr(
            "FLOW_OTOMATIS_IMPORT.json",
            json.dumps(_manifest()),
        )

    with pytest.raises(PackageSecurityError):
        EpisodePackageReader().load(package)


def _write_folder_package(
    root: Path,
    manifest: dict[str, object],
    *,
    prompt_files: dict[str, str] | None = None,
) -> Path:
    package_root = root / "EP001_STEVE_JOBS_COMPLETE"
    manifest_dir = package_root / "09_FLOW_PROMPTS_AND_TAKES"
    images_dir = package_root / "08_APPROVED_IMAGES"
    manifest_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    (manifest_dir / "FLOW_OTOMATIS_IMPORT.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    (images_dir / "EP001__IMAGE__SCENE_016__v1.0.png").write_bytes(b"synthetic-image-16")
    (images_dir / "EP001__IMAGE__SCENE_017__v1.0.png").write_bytes(b"synthetic-image-17")
    for relative_name, value in (prompt_files or {}).items():
        prompt_path = manifest_dir / relative_name
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(value, encoding="utf-8")
    return package_root


def test_missing_prompt_txt_reference_is_rejected_for_zip_before_persistence(
    tmp_path: Path,
) -> None:
    manifest = _manifest()
    scenes = manifest["scenes"]
    assert isinstance(scenes, list)
    scenes[0]["motion_prompt"] = "missing_prompt.txt"
    package = _write_package(tmp_path / "missing-prompt.zip", manifest)
    projects_root = tmp_path / "projects"
    service = EpisodeImportService(
        EpisodePackageReader(),
        SqliteWorkspaceRepository(projects_root),
    )

    with pytest.raises(PackageValidationError) as exc_info:
        service.import_package(package)

    assert exc_info.value.code == "PROMPT_FILE_MISSING"
    assert "SCENE_016" in str(exc_info.value)
    assert "missing_prompt.txt" in str(exc_info.value)
    assert not projects_root.exists()


def test_missing_prompt_txt_reference_is_rejected_for_folder(tmp_path: Path) -> None:
    manifest = _manifest()
    scenes = manifest["scenes"]
    assert isinstance(scenes, list)
    scenes[0]["motion_prompt"] = "missing_prompt.txt"
    package_root = _write_folder_package(tmp_path, manifest)

    with pytest.raises(PackageValidationError) as exc_info:
        EpisodePackageReader().load(package_root)

    assert exc_info.value.code == "PROMPT_FILE_MISSING"
    assert "SCENE_016" in str(exc_info.value)


def test_prompt_txt_empty_is_not_ready_and_valid_utf8_is_loaded(tmp_path: Path) -> None:
    manifest = _manifest()
    scenes = manifest["scenes"]
    assert isinstance(scenes, list)
    scenes[0]["motion_prompt"] = "scene16.txt"
    scenes[1]["motion_prompt"] = "scene17.txt"
    package_root = _write_folder_package(
        tmp_path,
        manifest,
        prompt_files={
            "scene16.txt": "",
            "scene17.txt": "Gerakan kamera lembut — identitas stabil.",
        },
    )

    draft = EpisodeImportService(
        EpisodePackageReader(),
        SqliteWorkspaceRepository(tmp_path / "projects"),
    ).validate(package_root)

    assert draft.scenes[0].motion_prompt == ""
    assert draft.scenes[0].readiness is SceneReadiness.MISSING_PROMPT
    assert draft.scenes[1].motion_prompt == "Gerakan kamera lembut — identitas stabil."
    assert draft.scenes[1].readiness is SceneReadiness.READY


def test_duplicate_import_is_rejected_without_changing_workspace_jobs_or_downloads(
    tmp_path: Path,
) -> None:
    projects_root = tmp_path / "projects"
    repository = SqliteWorkspaceRepository(projects_root)
    service = EpisodeImportService(EpisodePackageReader(), repository)
    original_package = _write_package(tmp_path / "original.zip", _manifest())
    original = service.import_package(original_package)

    now = datetime.now(UTC)
    job_repo = SqliteGenerationJobRepository(projects_root)
    original_scene = next(scene for scene in original.scenes if scene.scene_id == "SCENE_017")
    job = GenerationJob(
        job_id="EP001_STEVE_JOBS:SCENE_017:GENERATE",
        episode_id="EP001_STEVE_JOBS",
        scene_id="SCENE_017",
        target_duration_s=5.42,
        flow_duration_s=6,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file=original_scene.image_file,
        motion_prompt=original_scene.motion_prompt,
        model=original_scene.model,
        resolution=original_scene.resolution,
        aspect_ratio=original_scene.aspect_ratio,
        request_fingerprint="verified-duplicate-import-fixture",
    )
    job_repo.ensure_jobs((job,))
    claimed = job_repo.claim_next(
        "EP001_STEVE_JOBS",
        "duplicate-import-fixture-owner",
        lease_seconds=60,
    )
    assert claimed is not None
    generated = job_repo.mark_generated(
        job.job_id,
        "synthetic-result-017",
        "duplicate-import-fixture-owner",
    )

    download_repo = SqliteDownloadResultRepository(projects_root)
    downloaded = DownloadRecord(
        episode_id="EP001_STEVE_JOBS",
        scene_id="SCENE_017",
        state=DownloadState.DOWNLOADED,
        updated_at=now,
        output_path=str(tmp_path / "SCENE_017.mp4"),
        take=1,
    )
    download_repo.save(downloaded)

    replacement_manifest = _manifest()
    replacement_scenes = replacement_manifest["scenes"]
    assert isinstance(replacement_scenes, list)
    replacement_scenes[1]["target_duration_s"] = 2.0
    replacement_scenes[1]["trim_target_s"] = 2.0
    replacement_scenes[1]["motion_prompt"] = "Replacement prompt must never be persisted."
    replacement_package = _write_package(tmp_path / "replacement.zip", replacement_manifest)

    with pytest.raises(WorkspaceAlreadyExistsError) as exc_info:
        service.import_package(replacement_package)

    assert exc_info.value.episode_id == "EP001_STEVE_JOBS"
    assert repository.load("EP001_STEVE_JOBS") == original
    assert job_repo.list_for_episode("EP001_STEVE_JOBS") == (generated,)
    assert download_repo.list_for_episode("EP001_STEVE_JOBS") == (downloaded,)


def test_atomic_create_allows_only_one_concurrent_creator(tmp_path: Path) -> None:
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    package = _write_package(tmp_path / "concurrent.zip", _manifest())
    workspace = EpisodeImportService(EpisodePackageReader(), repository).validate(package)

    def create_once() -> str:
        try:
            repository.create(workspace)
        except WorkspaceAlreadyExistsError:
            return "duplicate"
        return "created"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _index: create_once(), range(2)))

    assert sorted(outcomes) == ["created", "duplicate"]
    assert repository.load(workspace.episode_id) == workspace
