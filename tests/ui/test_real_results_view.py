from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QTableWidget

from flow_otomatis.application.services import LocalResultsService
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.result import DownloadState, ProjectResults, SceneResult
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)
from flow_otomatis.presentation.main_window import MainWindow
from flow_otomatis.presentation.results_view import (
    build_results_view,
    verified_selected_mp4,
    verified_single_output_folder,
)


def _visible_text(window: MainWindow) -> str:
    values = [label.text() for label in window.findChildren(QLabel)]
    for table in window.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    values.append(item.text())
    return "\n".join(values)


@pytest.fixture
def ready_results(tmp_path: Path, qtbot):
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    job_repo = SqliteGenerationJobRepository(projects_root)
    download_repo = SqliteDownloadResultRepository(projects_root)
    writer = ResultManifestWriter(projects_root)
    service = LocalResultsService(workspace_repo, job_repo, download_repo, writer)

    now = datetime.now(UTC)
    scene = WorkspaceScene(
        scene_id="SCENE_001",
        image_file="SCENE_001.png",
        image_exists=True,
        motion_prompt="Slow push-in.",
        target_duration_s=3.8,
        recommended_flow_duration_s=4,
        selected_flow_duration_s=4,
        readiness=SceneReadiness.READY,
        trim_target_s=3.8,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )
    workspace = WorkspaceState(
        schema_version="1.0",
        episode_id="EP401_RESULTS_UI",
        project_name="Results UI Test",
        source_package_path=str(Path("package.zip")),
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )
    workspace_repo.save(workspace)
    job = GenerationJob(
        job_id="EP401_RESULTS_UI:SCENE_001:GENERATE",
        episode_id="EP401_RESULTS_UI",
        scene_id="SCENE_001",
        target_duration_s=3.8,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file=scene.image_file,
        motion_prompt=scene.motion_prompt,
        model=scene.model,
        resolution=scene.resolution,
        aspect_ratio=scene.aspect_ratio,
        request_fingerprint="verified-results-ui-fixture",
    )
    job_repo.ensure_jobs((job,))
    claimed = job_repo.claim_next(
        workspace.episode_id,
        "results-ui-owner",
        lease_seconds=60,
    )
    assert claimed is not None
    job_repo.mark_generated(job.job_id, "fake:SCENE_001", "results-ui-owner")
    output = tmp_path / "SCENE_001.mp4"
    output.write_bytes(b"synthetic-video")
    service.record_downloaded(workspace.episode_id, scene.scene_id, str(output))

    window = MainWindow(local_results_service=service)
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    return window, service, projects_root / workspace.episode_id / "project.sqlite3"


def test_real_hasil_view_exports_handoff_manifest(ready_results, qtbot) -> None:
    window, _service, _database = ready_results
    window.show_results_state()

    text = _visible_text(window)
    assert window.fixture_code == "REAL_RESULTS"
    assert "S001" in text
    assert "Selesai" in text
    assert "Tersimpan" in text
    assert "SCENE_001.mp4" in text

    button = next(
        item
        for item in window.findChildren(QPushButton)
        if item.text() == "Tandai Siap untuk Editing"
    )
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert window.last_result_manifest_path is not None
    assert window.last_result_manifest_path.is_file()


def test_t17_missing_video_displays_unavailable_and_blocks_export(tmp_path: Path, qtbot) -> None:
    root = tmp_path / "projects"
    workspaces = SqliteWorkspaceRepository(root)
    jobs = SqliteGenerationJobRepository(root)
    downloads = SqliteDownloadResultRepository(root)
    results = LocalResultsService(workspaces, jobs, downloads, ResultManifestWriter(root))
    now = datetime.now(UTC)
    scene = WorkspaceScene(
        scene_id="SCENE_001",
        image_file="SCENE_001.png",
        image_exists=True,
        motion_prompt="Slow pan.",
        target_duration_s=4.0,
        recommended_flow_duration_s=4,
        selected_flow_duration_s=4,
        readiness=SceneReadiness.READY,
        trim_target_s=4.0,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )
    workspace = WorkspaceState(
        schema_version="1.0",
        episode_id="EP402_MISSING",
        project_name="Missing Result UI",
        source_package_path="source.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )
    workspaces.save(workspace)
    job = GenerationJob(
        job_id="EP402_MISSING:SCENE_001:GENERATE",
        episode_id="EP402_MISSING",
        scene_id="SCENE_001",
        target_duration_s=4.0,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file=scene.image_file,
        motion_prompt=scene.motion_prompt,
        model=scene.model,
        resolution=scene.resolution,
        aspect_ratio=scene.aspect_ratio,
        request_fingerprint="fixture",
    )
    jobs.ensure_jobs((job,))
    assert jobs.claim_next(workspace.episode_id, "owner", lease_seconds=60)
    jobs.mark_generated(job.job_id, "remote:still-here", "owner")
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    results.record_downloaded(workspace.episode_id, scene.scene_id, str(video))
    video.unlink()

    window = MainWindow(local_results_service=results)
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    window.show_results_state()
    visible = _visible_text(window)
    assert "Tidak Tersedia" in visible
    assert "0/1" in visible
    assert window.fixture_code == "REAL_RESULTS"
    assert window.last_result_manifest_path is None
    # The frozen layout keeps its button; R03 must not wire a handoff action.
    matching = [
        button
        for button in window.findChildren(QPushButton)
        if button.text() == "Tandai Siap untuk Editing"
    ]
    for button in matching:
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert window.last_result_manifest_path is None


@pytest.mark.parametrize("damage", ["database", "timestamp", "take"])
def test_hasil_navigation_reports_unreadable_history_and_keeps_workspace(
    ready_results,
    qtbot,
    monkeypatch,
    damage: str,
) -> None:
    window, _service, database = ready_results
    if damage == "database":
        database.write_bytes(b"invalid sqlite")
    else:
        with sqlite3.connect(database) as connection:
            if damage == "timestamp":
                connection.execute("UPDATE download_results SET updated_at = 'invalid'")
            else:
                connection.execute("UPDATE download_results SET take = 'invalid'")
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[1:]))
    button = next(b for b in window.findChildren(QPushButton) if b.text().strip().endswith("Hasil"))
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert warnings and warnings[0][0] == "Hasil Tidak Dapat Dibuka"
    assert window.fixture_code == "REAL_WORKSPACE"
    assert not button.isChecked()
    assert window.current_workspace is not None
    assert window.last_result_manifest_path is None


def test_hasil_export_reports_write_failure_preserves_manifest_and_can_retry(
    ready_results,
    qtbot,
    monkeypatch,
) -> None:
    from flow_otomatis.infrastructure.filesystem import result_manifest_writer

    window, _service, _database = ready_results
    window.show_results_state()
    previous = window.export_current_result_manifest()
    before = hashlib.sha256(previous.read_bytes()).hexdigest()
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[1:]))
    button = next(
        b for b in window.findChildren(QPushButton) if b.text() == "Tandai Siap untuk Editing"
    )
    original_replace = result_manifest_writer.os.replace

    def deny_replace(*args):
        raise PermissionError("private-path-must-not-appear-in-dialog")

    monkeypatch.setattr(result_manifest_writer.os, "replace", deny_replace)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert warnings and warnings[0][0] == "Ekspor Hasil Gagal"
    assert "private-path" not in str(warnings)
    assert window.last_result_manifest_path is None
    assert hashlib.sha256(previous.read_bytes()).hexdigest() == before
    assert not list(previous.parent.glob("*.tmp"))
    assert window.fixture_code == "REAL_RESULTS"

    monkeypatch.setattr(result_manifest_writer.os, "replace", original_replace)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert window.last_result_manifest_path == previous
    assert len(warnings) == 1


def test_active_project_without_results_reader_shows_truthful_unavailable_ui(
    ready_results, qtbot
) -> None:
    window, _service, _database = ready_results
    original_workspace = window.current_workspace
    assert original_workspace is not None
    window.configure_production_shell()
    window._local_results_service = None

    window._open_navigation_item("Hasil")
    assert window.fixture_code == "REAL_RESULTS_UNAVAILABLE"
    assert window.current_workspace is original_workspace
    body = window._content_layout.itemAt(0).widget()
    assert body is not None
    assert body.objectName() == "RealResultsUnavailable"
    labels = " ".join(label.text() for label in body.findChildren(QLabel))
    assert "PEMBACA HASIL TIDAK TERSEDIA" in labels
    assert "belum tersedia" in labels
    assert "60/60" not in labels
    assert "EP001_SCENE" not in labels
    assert window._right_host.isHidden()
    back = body.findChild(QPushButton, "RealResultsUnavailableBack")
    assert back is not None and back.isEnabled()
    back.click()
    assert window.fixture_code == "REAL_WORKSPACE"
    assert window.current_workspace is original_workspace
    window.close()


def test_pending_result_rows_do_not_advertise_success_or_download(tmp_path, qtbot) -> None:
    now = datetime.now(UTC)
    pending = ProjectResults(
        episode_id="EP_PENDING_HASIL",
        project_name="Pending Results",
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
                updated_at=now,
            ),
        ),
    )
    sent: list[str] = []
    body = build_results_view(pending, on_export_manifest=lambda: sent.append("export"))
    qtbot.addWidget(body)
    table = next(t for t in body.findChildren(QTableWidget) if t.columnCount() == 6)
    assert table.rowCount() == 1
    assert [table.item(0, col).text() for col in (3, 4, 5)] == ["Belum", "Belum", "—"]
    text = " ".join(label.text() for label in body.findChildren(QLabel))
    assert "Status dari catatan proyek lokal" in text
    assert "Belum selesai" in text
    assert "Tidak ada laporan masalah" in text
    assert "Semua generation dan download selesai" not in text
    assert "60/60" not in text
    assert sent == []
    body.close()


def test_download_unavailable_does_not_display_ghost_output_filename(qtbot) -> None:
    now = datetime.now(UTC)
    state = ProjectResults(
        episode_id="EP_LOST_RESULT",
        project_name="Lost file",
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            SceneResult(
                scene_id="SCENE_001",
                target_duration_s=4.0,
                selected_flow_duration_s=4,
                trim_target_s=4.0,
                generate_state=GenerationJobState.GENERATED,
                remote_result_id="synthetic",
                download_state=DownloadState.UNAVAILABLE,
                output_path="/private/path/ghost-video.mp4",
                take=1,
                updated_at=now,
            ),
        ),
    )
    body = build_results_view(state, on_export_manifest=lambda: None)
    qtbot.addWidget(body)
    table = next(t for t in body.findChildren(QTableWidget) if t.columnCount() == 6)
    assert table.item(0, 4).text() == "Tidak Tersedia"
    assert table.item(0, 5).text() == "—"
    for button in body.findChildren(QPushButton):
        if button.text() in {"Retry Download Terpilih", "Buka Diagnostik"}:
            assert not button.isEnabled()
            assert "belum tersedia" in button.toolTip()
    body.close()


def test_hasil_diagnostics_button_opens_real_local_view_without_fake_provider(
    ready_results, qtbot
) -> None:
    window, _service, _database = ready_results
    workspace = window.current_workspace
    assert workspace is not None
    window.configure_production_shell()
    window.show_results_state()

    button = window.findChild(QPushButton, "RealResultsOpenDiagnostics")
    assert button is not None and button.isEnabled()
    assert "lokal" in button.toolTip()
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert window.fixture_code == "REAL_DIAGNOSTICS"
    assert window.current_workspace is workspace
    assert window._nav_buttons["Diagnostik"].isChecked()
    assert "Mode Lokal" in window._connection_badge.text()
    assert window.findChild(QTableWidget, "RealLocalDiagnosticsTable") is not None
    window.close()


def test_stale_hasil_callbacks_cannot_open_diagnostics_or_export_different_episode(
    ready_results, qtbot, monkeypatch
) -> None:
    window, _service, _database = ready_results
    workspace = window.current_workspace
    assert workspace is not None
    episode_id = workspace.episode_id
    exports: list[str] = []

    def export_spy() -> Path:
        exports.append("export")
        return Path("unused.json")

    monkeypatch.setattr(window, "export_current_result_manifest", export_spy)
    window.show_results_state()
    # Navigating away makes all saved callback closures from Hasil stale.
    window.show_workspace_state(workspace)
    window._open_diagnostics_from_results(episode_id)
    window._export_result_manifest_from_ui(episode_id)
    assert window.fixture_code == "REAL_WORKSPACE"
    assert exports == []
    assert window.last_result_manifest_path is None

    # The episode guard also applies if the app is currently showing Hasil
    # for some other selected Workspace.
    window.show_results_state()
    window._open_diagnostics_from_results("EP_OTHER")
    window._export_result_manifest_from_ui("EP_OTHER")
    assert window.fixture_code == "REAL_RESULTS"
    assert exports == []
    window.close()


def test_pending_results_mounts_actionable_local_diagnostics_without_generate(qtbot) -> None:
    now = datetime.now(UTC)
    pending = ProjectResults(
        episode_id="EP_PENDING_DIAGNOSTICS",
        project_name="Pending local results",
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
                updated_at=now,
            ),
        ),
    )
    opened: list[str] = []
    view = build_results_view(
        pending,
        on_export_manifest=lambda: opened.append("export"),
        on_open_diagnostics=lambda: opened.append("diagnostics"),
    )
    qtbot.addWidget(view)
    action = view.findChild(QPushButton, "RealResultsOpenDiagnostics")
    assert action is not None and action.isEnabled()
    qtbot.mouseClick(action, Qt.MouseButton.LeftButton)
    assert opened == ["diagnostics"]
    assert "Selesai" not in action.text()
    assert not any(
        button.isEnabled()
        for button in view.findChildren(QPushButton)
        if button.text() == "Tandai Siap untuk Editing"
    )
    view.close()


def test_hasil_refresh_rereads_local_snapshot_and_clears_stale_manifest(
    ready_results, qtbot, monkeypatch
) -> None:
    window, service, _database = ready_results
    window.show_results_state()
    workspace = window.current_workspace
    assert workspace is not None
    previous_export = window.export_current_result_manifest()
    assert previous_export.is_file()
    scanned: list[str] = []
    original_snapshot = service.snapshot

    def tracked_snapshot(episode_id: str):
        scanned.append(episode_id)
        return original_snapshot(episode_id)

    monkeypatch.setattr(service, "snapshot", tracked_snapshot)
    refresh = window.findChild(QPushButton, "RealResultsRefresh")
    assert refresh is not None and refresh.isEnabled()
    assert "lokal" in refresh.toolTip()
    qtbot.mouseClick(refresh, Qt.MouseButton.LeftButton)
    assert scanned == [workspace.episode_id]
    assert window.fixture_code == "REAL_RESULTS"
    assert window.last_result_manifest_path is None
    assert "SCENE_001.mp4" in _visible_text(window)
    window.close()


def test_hasil_refresh_failure_keeps_existing_page_and_redacts_storage_errors(
    ready_results, qtbot, monkeypatch
) -> None:
    window, _service, database = ready_results
    window.show_results_state()
    refresh = window.findChild(QPushButton, "RealResultsRefresh")
    assert refresh is not None
    before = _visible_text(window)
    database.write_bytes(b"invalid-sqlite-diagnostic-secret")
    warnings: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _window, title, detail: warnings.append((title, detail)),
    )
    qtbot.mouseClick(refresh, Qt.MouseButton.LeftButton)
    assert window.fixture_code == "REAL_RESULTS"
    assert warnings and warnings[0][0] == "Hasil Tidak Dapat Diperbarui"
    assert "invalid-sqlite" not in str(warnings)
    assert _visible_text(window) == before
    window.close()


def test_stale_hasil_refresh_callback_cannot_reload_after_navigation(
    ready_results, qtbot, monkeypatch
) -> None:
    window, service, _database = ready_results
    workspace = window.current_workspace
    assert workspace is not None
    window.show_results_state()
    window.show_workspace_state(workspace)
    called: list[str] = []
    monkeypatch.setattr(service, "snapshot", lambda episode_id: called.append(episode_id))
    window._refresh_results_from_ui(workspace.episode_id)
    assert window.fixture_code == "REAL_WORKSPACE"
    assert called == []
    window.close()


def test_real_hasil_open_verified_local_output_folder(ready_results, qtbot, monkeypatch) -> None:
    window, service, _database = ready_results
    window.show_results_state()
    captured: list[object] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: captured.append(url) or True)
    button = window.findChild(QPushButton, "RealResultsOpenFolder")
    assert button is not None and button.isEnabled()
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert len(captured) == 1
    assert captured[0].isLocalFile()
    latest = service.snapshot(window.current_workspace.episode_id)
    assert Path(captured[0].toLocalFile()) == verified_single_output_folder(latest)
    assert window.fixture_code == "REAL_RESULTS"
    window.close()


def test_results_open_folder_fails_closed_if_mp4_disappears(
    ready_results, qtbot, monkeypatch
) -> None:
    window, service, _database = ready_results
    window.show_results_state()
    before = service.snapshot(window.current_workspace.episode_id)
    original = Path(before.scenes[0].output_path)
    original.unlink()
    opened: list[str] = []
    warnings: list[tuple[str, str]] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(str(url)) or True)
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _window, title, detail: warnings.append((title, detail))
    )
    button = window.findChild(QPushButton, "RealResultsOpenFolder")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert not opened
    assert warnings and warnings[0][0] == "Folder Output Tidak Tersedia"
    assert "private" not in warnings[0][1].lower()
    window.close()


def test_results_open_folder_ignores_stale_page_callback_after_refresh(
    ready_results, monkeypatch
) -> None:
    window, _service, _database = ready_results
    window.show_results_state()
    prior = window._last_results_snapshot
    assert prior is not None
    window.show_results_state()
    assert window._last_results_snapshot is not prior
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(str(url)) or True)
    window._open_result_folder_from_ui(prior)
    assert opened == []
    window.close()


def test_results_open_folder_does_not_choose_between_distinct_directories(
    ready_results, tmp_path, qtbot
) -> None:
    window, service, _database = ready_results
    actual = service.snapshot(window.current_workspace.episode_id)
    first = actual.scenes[0]
    second_dir = tmp_path / "different_folder"
    second_dir.mkdir()
    other_file = second_dir / "SCENE_002.mp4"
    other_file.write_bytes(b"valid-other-video")
    other = replace(first, scene_id="SCENE_002", output_path=str(other_file))
    mixed = replace(actual, scenes=(first, other))
    assert verified_single_output_folder(mixed) is None

    body = build_results_view(
        mixed,
        on_export_manifest=lambda: None,
        on_open_folder=lambda: None,
    )
    qtbot.addWidget(body)
    button = body.findChild(QPushButton, "RealResultsOpenFolder")
    assert button is not None and not button.isEnabled()
    assert "beberapa folder" in button.toolTip()
    body.close()
    window.close()


def test_results_open_folder_windows_failure_is_redacted(ready_results, qtbot, monkeypatch) -> None:
    window, _service, _database = ready_results
    window.show_results_state()
    messages: list[tuple[str, str]] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: False)
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _window, title, detail: messages.append((title, detail))
    )
    button = window.findChild(QPushButton, "RealResultsOpenFolder")
    assert button is not None and button.isEnabled()
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert messages == [
        (
            "Folder Output Tidak Dapat Dibuka",
            "Windows belum dapat membuka folder MP4 yang tersedia.",
        )
    ]
    window.close()


def test_play_selected_local_mp4_opens_exact_verified_scene(
    ready_results, qtbot, monkeypatch
) -> None:
    window, service, _database = ready_results
    window.show_results_state()
    play = window.findChild(QPushButton, "RealResultsOpenSelectedVideo")
    assert play is not None and not play.isEnabled()
    table = next(t for t in window.findChildren(QTableWidget) if t.columnCount() == 6)
    table.selectRow(0)
    assert play.isEnabled()
    assert "default Windows" in play.toolTip()
    captured: list[object] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: captured.append(url) or True)
    qtbot.mouseClick(play, Qt.MouseButton.LeftButton)
    assert len(captured) == 1
    assert captured[0].isLocalFile()
    results = service.snapshot(window.current_workspace.episode_id)
    assert Path(captured[0].toLocalFile()) == verified_selected_mp4(results, "SCENE_001")
    assert window.fixture_code == "REAL_RESULTS"
    window.close()


def test_play_selected_local_mp4_requires_download_and_one_row(qtbot) -> None:
    now = datetime.now(UTC)
    pending = ProjectResults(
        episode_id="EP_PLAY_PENDING",
        project_name="Pending",
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
                updated_at=now,
            ),
        ),
    )
    selected: list[str] = []
    view = build_results_view(
        pending,
        on_export_manifest=lambda: None,
        on_open_video=lambda scene_id: selected.append(scene_id),
    )
    qtbot.addWidget(view)
    button = view.findChild(QPushButton, "RealResultsOpenSelectedVideo")
    table = next(t for t in view.findChildren(QTableWidget) if t.columnCount() == 6)
    assert button is not None and not button.isEnabled()
    table.selectRow(0)
    assert not button.isEnabled()
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert selected == []
    assert verified_selected_mp4(pending, "SCENE_001") is None
    view.close()


def test_play_local_mp4_disappearance_is_rejected_after_selection(
    ready_results, qtbot, monkeypatch
) -> None:
    window, service, _database = ready_results
    window.show_results_state()
    play = window.findChild(QPushButton, "RealResultsOpenSelectedVideo")
    table = next(t for t in window.findChildren(QTableWidget) if t.columnCount() == 6)
    table.selectRow(0)
    assert play is not None and play.isEnabled()
    results = service.snapshot(window.current_workspace.episode_id)
    Path(results.scenes[0].output_path).unlink()
    opened: list[str] = []
    warnings: list[tuple[str, str]] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(str(url)) or True)
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _window, title, msg: warnings.append((title, msg))
    )
    qtbot.mouseClick(play, Qt.MouseButton.LeftButton)
    assert opened == []
    assert warnings and warnings[0][0] == "Video Lokal Tidak Tersedia"
    window.close()


def test_play_local_mp4_ignores_stale_result_page_after_refresh(ready_results, monkeypatch) -> None:
    window, _service, _database = ready_results
    window.show_results_state()
    old = window._last_results_snapshot
    assert old is not None
    window.show_results_state()
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(str(url)) or True)
    window._open_result_video_from_ui(old, "SCENE_001")
    assert opened == []
    window.show_workspace_state(window.current_workspace)
    window._open_result_video_from_ui(old, "SCENE_001")
    assert opened == []
    window.close()


def test_play_local_mp4_os_failure_is_redacted(ready_results, qtbot, monkeypatch) -> None:
    window, _service, _database = ready_results
    window.show_results_state()
    play = window.findChild(QPushButton, "RealResultsOpenSelectedVideo")
    table = next(t for t in window.findChildren(QTableWidget) if t.columnCount() == 6)
    table.selectRow(0)
    assert play is not None and play.isEnabled()
    warning: list[tuple[str, str]] = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: False)
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _window, title, msg: warning.append((title, msg))
    )
    qtbot.mouseClick(play, Qt.MouseButton.LeftButton)
    assert warning == [
        (
            "Pemutar Video Tidak Tersedia",
            "Windows tidak dapat membuka MP4 dengan aplikasi pemutar default.",
        )
    ]
    window.close()


def test_selected_video_disallows_file_symlink(ready_results, monkeypatch) -> None:
    window, service, _database = ready_results
    results = service.snapshot(window.current_workspace.episode_id)
    real_file = Path(results.scenes[0].output_path)
    # CI Windows may not allow symlink creation; simulate the reparse point.
    monkeypatch.setattr(Path, "is_symlink", lambda path: path == real_file)
    assert verified_selected_mp4(results, "SCENE_001") is None
    assert verified_selected_mp4(results, "nonexistent") is None
    window.close()


def test_play_selected_mp4_uses_exact_second_scene_not_first(
    ready_results, tmp_path, qtbot
) -> None:
    window, service, _database = ready_results
    snapshot = service.snapshot(window.current_workspace.episode_id)
    first = snapshot.scenes[0]
    second_output = tmp_path / "second_scene.mp4"
    second_output.write_bytes(b"second-local-video")
    second = replace(first, scene_id="SCENE_002", output_path=str(second_output))
    combined = replace(snapshot, scenes=(first, second))
    selected: list[str] = []
    view = build_results_view(
        combined,
        on_export_manifest=lambda: None,
        on_open_video=lambda scene_id: selected.append(scene_id),
    )
    qtbot.addWidget(view)
    table = next(t for t in view.findChildren(QTableWidget) if t.columnCount() == 6)
    play = view.findChild(QPushButton, "RealResultsOpenSelectedVideo")
    assert play is not None and not play.isEnabled()
    table.selectRow(1)
    assert play.isEnabled()
    qtbot.mouseClick(play, Qt.MouseButton.LeftButton)
    assert selected == ["SCENE_002"]
    table.clearSelection()
    assert not play.isEnabled()
    view.close()
    window.close()
