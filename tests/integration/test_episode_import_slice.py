from __future__ import annotations

import hashlib
import json
import sqlite3
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.application.services import EpisodeImportService, ScenePlanningService
from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.domain.errors import (
    InternalInvariantError,
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


def test_import_pins_sha256_and_detects_same_path_image_modification(tmp_path: Path) -> None:
    """Changing bytes at a valid source path must not inherit initial approval."""
    package = _write_folder_package(tmp_path / "episode", _manifest())
    reader = EpisodePackageReader()
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    service = EpisodeImportService(reader, repository, image_verifier=reader)
    workspace = service.import_package(package)
    original = repository.load(workspace.episode_id)
    assert original == workspace
    expected_hash = hashlib.sha256(b"synthetic-image-17").hexdigest()
    assert workspace.scenes[1].image_sha256_imported == expected_hash
    assert len(workspace.scenes[0].image_sha256_imported or "") == 64

    initial = prepare_local_scene_preflight(workspace, image_verifier=reader)
    assert initial["baseline_match_count"] == 2
    assert initial["baseline_mismatch_count"] == 0
    assert initial["baseline_missing_count"] == 0
    assert initial["image_baselines_verified"] is True

    image = package / "08_APPROVED_IMAGES" / "EP001__IMAGE__SCENE_017__v1.0.png"
    image.write_bytes(b"modified-image-17")
    changed = prepare_local_scene_preflight(workspace, image_verifier=reader)
    assert changed["baseline_match_count"] == 1
    assert changed["baseline_mismatch_count"] == 1
    assert changed["image_baselines_verified"] is False
    assert changed["held_count"] == 2
    assert any("GAMBAR BERUBAH SEJAK IMPOR" in row["issues"] for row in changed["held"])
    assert "modified-image" not in json.dumps(changed)
    assert str(tmp_path) not in json.dumps(changed)
    assert repository.load(workspace.episode_id) == original

    planning = ScenePlanningService(reader, repository)
    planning.select_flow_duration(workspace.episode_id, "SCENE_016", 8)
    reloaded = repository.load(workspace.episode_id)
    assert reloaded is not None
    assert reloaded.scenes[1].image_sha256_imported == expected_hash


def test_legacy_workspace_loads_without_baseline_and_migrates_only_on_write(
    tmp_path: Path,
) -> None:
    """Old projects must not be rewritten or assigned fake historical digests."""
    package = _write_package(tmp_path / "episode.zip", _manifest())
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    reader = EpisodePackageReader()
    legacy = EpisodeImportService(reader, repository).import_package(package)
    db = tmp_path / "projects" / legacy.episode_id / "project.sqlite3"

    # Emulate the previously released scenes schema with no digest column.
    with sqlite3.connect(db) as connection:
        connection.execute("ALTER TABLE scenes DROP COLUMN image_sha256_imported")
    initial_bytes = db.read_bytes()
    restored = repository.load(legacy.episode_id)
    assert restored == legacy
    assert all(scene.image_sha256_imported is None for scene in restored.scenes)
    assert db.read_bytes() == initial_bytes

    report = prepare_local_scene_preflight(restored, image_verifier=reader)
    assert report["baseline_missing_count"] == 2
    assert report["baseline_match_count"] == 0
    assert report["image_baselines_verified"] is False
    assert "GAMBAR BERUBAH SEJAK IMPOR" not in json.dumps(report)

    planner = ScenePlanningService(reader, repository)
    updated = planner.select_flow_duration(legacy.episode_id, "SCENE_016", 8)
    assert updated.scenes[0].selected_flow_duration_s == 8
    assert all(scene.image_sha256_imported is None for scene in updated.scenes)
    with sqlite3.connect(db) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(scenes)")}
    assert "image_sha256_imported" in columns


@pytest.mark.parametrize(
    "extra_name",
    [
        "EP001_STEVE_JOBS_COMPLETE/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
        "EP001_STEVE_JOBS_COMPLETE/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__V1.0.PNG",
    ],
)
def test_ambiguous_zip_image_entries_never_import_or_hash(tmp_path: Path, extra_name: str) -> None:
    package = _write_package(tmp_path / "duplicate_images.zip", _manifest())
    # zipfile deliberately allows duplicate names; a read-by-name then resolves
    # the last member, which is not an acceptable source for pinned SHA-256.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(package, "a") as archive:
            archive.writestr(extra_name, b"shadow-image-content")
    reader = EpisodePackageReader()
    with pytest.raises(PackageSecurityError, match="duplicate or ambiguous"):
        reader.load(package)
    with pytest.raises(PackageSecurityError, match="duplicate or ambiguous"):
        reader.image_digest(
            package,
            "SCENE_016",
            "../08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
        )
    projects = tmp_path / "projects"
    with pytest.raises(PackageSecurityError, match="duplicate or ambiguous"):
        EpisodeImportService(
            reader,
            SqliteWorkspaceRepository(projects),
            image_verifier=reader,
        ).import_package(package)
    assert not projects.exists()


def test_workspace_concurrent_edits_cannot_both_commit_from_same_revision(
    tmp_path: Path,
) -> None:
    """The second editor must receive a conflict, never silently lose a change."""
    package = _write_package(tmp_path / "two_editors.zip", _manifest())
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    original = EpisodeImportService(EpisodePackageReader(), repository).import_package(package)

    def candidate(duration: int):
        first = replace(
            original.scenes[0],
            selected_flow_duration_s=duration,
            readiness=SceneReadiness.READY,
        )
        return replace(original, scenes=(first, original.scenes[1]))

    choices = (candidate(8), candidate(10))

    def write_once(workspace):
        try:
            repository.update(workspace, expected_workspace=original)
        except InternalInvariantError:
            return "conflict"
        return "saved"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(write_once, choices))
    assert sorted(outcomes) == ["conflict", "saved"]

    saved = repository.load(original.episode_id)
    assert saved in choices
    assert saved is not None
    assert saved.scenes[1] == original.scenes[1]
    other = choices[1] if saved == choices[0] else choices[0]
    with pytest.raises(InternalInvariantError, match="berubah saat disimpan"):
        repository.update(other, expected_workspace=original)
    assert repository.load(original.episode_id) == saved

    # After an explicit refresh, another edit is allowed without data loss.
    follow_up = replace(
        saved,
        scenes=(
            saved.scenes[0],
            replace(saved.scenes[1], motion_prompt="Fresh second editor change"),
        ),
    )
    repository.update(follow_up, expected_workspace=saved)
    assert repository.load(saved.episode_id) == follow_up


def test_conflicting_write_to_legacy_workspace_does_not_fabricate_checksum(
    tmp_path: Path,
) -> None:
    """A stale write may not migrate/modify an older project's database."""
    package = _write_package(tmp_path / "legacy_conflict.zip", _manifest())
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    original = EpisodeImportService(EpisodePackageReader(), repository).import_package(package)
    db = tmp_path / "projects" / original.episode_id / "project.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("ALTER TABLE scenes DROP COLUMN image_sha256_imported")
    old = repository.load(original.episode_id)
    assert old is not None
    first = replace(
        old,
        scenes=(
            replace(old.scenes[0], selected_flow_duration_s=8, readiness=SceneReadiness.READY),
            old.scenes[1],
        ),
    )
    repository.update(first, expected_workspace=old)
    current = repository.load(old.episode_id)
    assert current == first

    before = db.read_bytes()
    with pytest.raises(InternalInvariantError, match="berubah saat disimpan"):
        repository.update(old, expected_workspace=old)
    assert repository.load(old.episode_id) == current
    assert db.read_bytes() == before
    assert all(scene.image_sha256_imported is None for scene in current.scenes)
