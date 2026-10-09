"""Validate all approved E12-02 UIX states without any live Google service."""

from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedLayout,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.presentation.credit_uix_preview import (
    SCENARIO_BY_ID,
    UIX_SCENARIOS,
    CreditUixDialog,
)
from flow_otomatis.presentation.main_window import MainWindow


def test_all_22_owner_approved_states_render_and_never_offer_live(qtbot) -> None:
    dialog = CreditUixDialog()
    qtbot.addWidget(dialog)
    assert len(UIX_SCENARIOS) == 22
    assert len(SCENARIO_BY_ID) == 22
    for scenario in UIX_SCENARIOS:
        dialog.set_state(scenario.code)
        assert dialog.current_state == scenario.code
        assert not dialog.live_dispatch_enabled
        table = dialog.findChild(QTableWidget, "UixDetailTable")
        assert table is not None
        assert table.rowCount() > 0
        live = dialog.findChild(QPushButton, "UixLiveGenerate")
        assert live is not None
        assert not live.isEnabled()
        assert dialog.findChild(QComboBox, "UixStateSelector").currentData() == scenario.code
    dialog.close()


def test_local_approval_never_permits_live_dispatch(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-04-A")
    qtbot.addWidget(dialog)
    check = dialog.findChild(QCheckBox, "UixSimulationApproval")
    approve = dialog.findChild(QPushButton, "UixSimulationFreeze")
    assert check is not None
    assert approve is not None
    assert not approve.isEnabled()
    check.setChecked(True)
    assert approve.isEnabled()
    approve.click()
    assert dialog._last_local_plan_approved is True
    assert not dialog.live_dispatch_enabled
    assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.set_state("UIX-08-B")
    assert dialog._last_local_plan_approved is False
    dialog.close()


def test_recalculation_is_local_and_keeps_simulation_flag(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-A")
    qtbot.addWidget(dialog)
    before = dialog._preview.copy()
    dialog.recalculate_offline()
    assert dialog._preview == before
    assert dialog._preview["mode"] == "OFFLINE_SIMULATION"
    assert dialog._preview["provider_evidence"] == "NONE"
    assert dialog._preview["live_dispatch_allowed"] is False
    dialog.close()


def test_navigation_groups_match_22_screens(qtbot) -> None:
    dialog = CreditUixDialog()
    qtbot.addWidget(dialog)
    group = dialog.findChild(QComboBox, "UixGroupSelector")
    states = dialog.findChild(QComboBox, "UixStateSelector")
    assert group is not None and states is not None
    assert group.count() == 9
    for index in range(9):
        group.setCurrentIndex(index)
        assert states.count() == sum(
            item.code.startswith(f"UIX-{index + 1:02}-") for item in UIX_SCENARIOS
        )
    dialog.close()


def test_each_approved_variant_has_safe_contextual_navigation(qtbot) -> None:
    dialog = CreditUixDialog()
    qtbot.addWidget(dialog)
    assert len(UIX_SCENARIOS) == 22
    for scenario in UIX_SCENARIOS:
        routes = dialog._actions_for(scenario.code)
        assert len(routes) == 2
        assert all(target in SCENARIO_BY_ID for _label, target in routes)
        dialog.set_state(scenario.code)
        assert dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled() is False
    dialog.close()


def test_no_eligible_profiles_never_looks_like_success(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-C")
    qtbot.addWidget(dialog)
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 12
    assert all(rows.item(i, 4).text() == "TIDAK ADA AKUN LAYAK" for i in range(12))
    assert all(rows.item(i, 1).text() == "—" for i in range(12))
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_partial_budget_and_stale_plan_show_separate_statuses(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-B")
    qtbot.addWidget(dialog)
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 12
    assert sum(rows.item(i, 4).text() == "SIMULASI" for i in range(12)) == 8
    assert sum(rows.item(i, 4).text() == "BELUM DIALOKASIKAN" for i in range(12)) == 4

    dialog.set_state("UIX-04-B")
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 3
    assert "HITUNG ULANG" in [rows.item(i, 3).text() for i in range(rows.rowCount())]
    dialog.close()


def test_uncertain_submit_remains_held_and_handoff_never_claims_real_mp4(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-05-C")
    qtbot.addWidget(dialog)
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.item(0, 2).text() == "SUBMIT_UNCERTAIN"
    assert "HELD" in rows.item(0, 3).text()

    dialog.set_state("UIX-09-B")
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 12
    assert all(rows.item(i, 3).text() == "TIDAK ADA MP4 NYATA" for i in range(12))
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_sidebar_preserves_seven_original_routes_as_non_live_labels(qtbot) -> None:
    from PySide6.QtWidgets import QFrame, QLabel

    dialog = CreditUixDialog()
    qtbot.addWidget(dialog)
    sidebar = dialog.findChild(QFrame, "UixSidebar")
    dock = dialog.findChild(QFrame, "UixRightDock")
    assert sidebar is not None
    assert dock is not None
    assert sidebar.width() == 216
    assert dock.width() == 376
    routes = sidebar.findChildren(QLabel, "UixSidebarRoute")
    assert [r.text().strip() for r in routes] == [
        "Beranda",
        "Workspace",
        "Hasil",
        "Profil Google",
        "Gemini Keys",
        "Diagnostik",
        "Pengaturan",
    ]
    dialog.close()


def test_search_filters_visible_rows_and_updates_readonly_dock(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-05-C")
    qtbot.addWidget(dialog)
    search = dialog.findChild(QLineEdit, "UixTableSearch")
    table = dialog.findChild(QTableWidget, "UixDetailTable")
    inspector = dialog.findChild(QLabel, "UixDockSelectedRow")
    count = dialog.findChild(QLabel, "UixFilterCount")
    assert search is not None and table is not None
    assert inspector is not None and count is not None
    assert table.rowCount() == 2

    search.setText("submit_uncertain")
    assert not table.isRowHidden(0)
    assert table.isRowHidden(1)
    assert count.text() == "1/2 baris (contoh)"
    assert "SCENE_008" in inspector.text()
    assert "SUBMIT_UNCERTAIN" in inspector.text()
    assert not dialog.live_dispatch_enabled

    search.setText("does-not-exist")
    assert all(table.isRowHidden(row) for row in range(2))
    assert count.text() == "0/2 baris (contoh)"
    assert "Tidak ada baris" in inspector.text()

    search.clear()
    assert not any(table.isRowHidden(row) for row in range(2))
    assert count.text() == "2/2 baris (contoh)"
    dialog.close()


def test_state_switch_resets_search_and_inspector_to_current_table(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-C")
    qtbot.addWidget(dialog)
    search = dialog.findChild(QLineEdit, "UixTableSearch")
    assert search is not None
    search.setText("SCENE_005")
    dialog.set_state("UIX-07-B")
    current_search = dialog.findChild(QLineEdit, "UixTableSearch")
    assert current_search is not None
    assert current_search is not search
    assert current_search.text() == ""
    table = dialog.findChild(QTableWidget, "UixDetailTable")
    assert table.rowCount() == 12
    assert not table.isRowHidden(0)
    inspector = dialog.findChild(QLabel, "UixDockSelectedRow")
    assert "SCENE_001" in inspector.text()
    assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.close()


def test_tariff_change_rejects_stale_plan_and_requires_reapproval(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-08-A")
    qtbot.addWidget(dialog)
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 5
    decisions = [rows.item(i, 3).text() for i in range(rows.rowCount())]
    assert "HITUNG ULANG" in decisions
    assert "MINTA ULANG" in decisions
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_unverified_provider_policy_disables_live_and_exposes_all_gates(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-08-B")
    qtbot.addWidget(dialog)
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 5
    statuses = [rows.item(i, 2).text() for i in range(rows.rowCount())]
    assert statuses.count("BELUM TERVERIFIKASI") == 2
    assert "BELUM LULUS" in statuses
    gate_names = [rows.item(i, 0).text() for i in range(rows.rowCount())]
    assert any(name.startswith("G1") for name in gate_names)
    assert any(name.startswith("G5") for name in gate_names)
    assert any(name.startswith("G6") for name in gate_names)
    assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.close()


def _workspace_with_mixed_real_scenes() -> WorkspaceState:
    examples = (
        ("SCENE_001", True, "Pan over an ancient map", 8, SceneReadiness.READY),
        ("SCENE_002", False, "Missing artwork", 6, SceneReadiness.MISSING_IMAGE),
        (
            "SCENE_003",
            True,
            "Slow zoom with clean lighting",
            None,
            SceneReadiness.NEEDS_DURATION_SELECTION,
        ),
    )
    scenes = tuple(
        WorkspaceScene(
            scene_id=scene_id,
            image_file=f"C:/private/frames/{scene_id}.png",
            image_exists=has_image,
            motion_prompt=prompt,
            target_duration_s=5.5,
            recommended_flow_duration_s=6,
            selected_flow_duration_s=chosen_duration,
            readiness=readiness,
            trim_target_s=5.5,
            model="Omni Flash 1.1",
            resolution="720p",
            aspect_ratio="16:9",
        )
        for scene_id, has_image, prompt, chosen_duration, readiness in examples
    )
    now = datetime(2026, 10, 9, tzinfo=UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP-LOCAL-1",
        project_name="Read-only local movie",
        source_package_path="C:/private/secret/source.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=scenes,
    )


def test_real_workspace_shows_actual_scene_readiness_across_every_ui_state(qtbot) -> None:
    source = _workspace_with_mixed_real_scenes()
    before = repr(source)
    dialog = CreditUixDialog(workspace=source, initial_state="UIX-01-A")
    qtbot.addWidget(dialog)
    selector = dialog.findChild(QComboBox, "UixDataSourceSelector")
    assert selector is not None
    assert selector.currentData() == "local"
    table = dialog.findChild(QTableWidget, "UixDetailTable")
    assert table.rowCount() == 3
    assert table.columnCount() == 6
    assert table.item(0, 0).text() == "SCENE_001"
    assert table.item(1, 5).text() == "GAMBAR HILANG"
    assert table.item(2, 5).text() == "PILIH DURASI"
    assert "3 baris (lokal)" in dialog.findChild(QLabel, "UixFilterCount").text()

    for scenario in UIX_SCENARIOS:
        dialog.set_state(scenario.code)
        table = dialog.findChild(QTableWidget, "UixDetailTable")
        assert table.rowCount() == 3
        assert table.item(0, 0).text() == "SCENE_001"
        assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    assert repr(source) == before
    dialog.close()


def test_workspace_demo_switch_never_blends_project_with_fake_budget(qtbot) -> None:
    workspace = _workspace_with_mixed_real_scenes()
    dialog = CreditUixDialog(workspace=workspace, initial_state="UIX-04-A")
    qtbot.addWidget(dialog)
    selector = dialog.findChild(QComboBox, "UixDataSourceSelector")
    assert dialog._using_local_inputs()
    assert dialog.findChild(QCheckBox, "UixSimulationApproval") is None
    scan = dialog._report_payload()
    assert scan["mode"] == "LOCAL_SCENE_READINESS_REPORT"
    assert scan["scene_count"] == 3
    assert scan["ready_count"] == 1
    assert scan["needs_duration_selection"] == 1
    assert scan["blocking_count"] == 1
    assert "profiles" not in scan
    assert "simulated_balance" not in str(scan)
    assert "source.zip" not in str(scan)
    assert "Pan over an ancient map" not in str(scan)
    assert "C:/private" not in str(scan)
    assert scan["live_dispatch_allowed"] is False

    selector.setCurrentIndex(selector.findData("demo"))
    assert not dialog._using_local_inputs()
    assert dialog.findChild(QTableWidget, "UixDetailTable").rowCount() == 12
    assert dialog.findChild(QCheckBox, "UixSimulationApproval") is not None
    report = dialog._report_payload()
    assert report["mode"] == "OFFLINE_SIMULATION"
    assert report["provider_evidence"] == "NONE"
    assert "EP-LOCAL-1" not in str(report)
    assert "C:/private" not in str(report)

    selector.setCurrentIndex(selector.findData("local"))
    assert dialog.findChild(QCheckBox, "UixSimulationApproval") is None
    assert dialog._report_payload()["mode"] == "LOCAL_SCENE_READINESS_REPORT"
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_empty_workspace_is_safe_and_zero_count_not_fake_success(qtbot) -> None:
    from dataclasses import replace

    empty = replace(_workspace_with_mixed_real_scenes(), scenes=())
    dialog = CreditUixDialog(workspace=empty, initial_state="UIX-09-B")
    qtbot.addWidget(dialog)
    table = dialog.findChild(QTableWidget, "UixDetailTable")
    assert table.rowCount() == 0
    assert dialog._report_payload()["scene_count"] == 0
    assert dialog._report_payload()["ready_count"] == 0
    assert "0 baris (lokal)" in dialog.findChild(QLabel, "UixFilterCount").text()
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_local_readiness_filters_and_open_scene_work_without_live(qtbot) -> None:
    dialog = CreditUixDialog(
        workspace=_workspace_with_mixed_real_scenes(), initial_state="UIX-01-A"
    )
    qtbot.addWidget(dialog)
    status = dialog.findChild(QComboBox, "UixReadinessFilter")
    search = dialog.findChild(QLineEdit, "UixTableSearch")
    table = dialog.findChild(QTableWidget, "UixDetailTable")
    count = dialog.findChild(QLabel, "UixFilterCount")
    open_scene = dialog.findChild(QPushButton, "UixOpenSceneInWorkspace")
    assert status is not None and open_scene is not None
    assert status.count() == 7
    assert table.rowCount() == 3

    status.setCurrentIndex(status.findData("PROBLEM"))
    assert count.text() == "1/3 baris (lokal)"
    assert table.isRowHidden(0) and not table.isRowHidden(1)
    assert table.isRowHidden(2)
    assert open_scene.isEnabled()
    assert not dialog.live_dispatch_enabled

    search.setText("SCENE_001")
    assert count.text() == "0/3 baris (lokal)"
    assert not open_scene.isEnabled()
    assert dialog.requested_scene_id is None

    search.clear()
    table.setCurrentCell(1, 0)
    assert open_scene.isEnabled()
    open_scene.click()
    assert dialog.requested_scene_id == "SCENE_002"
    assert dialog.result() == dialog.DialogCode.Accepted


def test_demo_cannot_request_scene_and_local_filter_does_not_leak(qtbot) -> None:
    dialog = CreditUixDialog(workspace=_workspace_with_mixed_real_scenes())
    qtbot.addWidget(dialog)
    source = dialog.findChild(QComboBox, "UixDataSourceSelector")
    status = dialog.findChild(QComboBox, "UixReadinessFilter")
    status.setCurrentIndex(status.findData("PILIH DURASI"))
    assert dialog.findChild(QTableWidget, "UixDetailTable").isRowHidden(0)

    source.setCurrentIndex(source.findData("demo"))
    assert dialog.findChild(QComboBox, "UixReadinessFilter") is None
    assert dialog.findChild(QPushButton, "UixOpenSceneInWorkspace") is None
    assert dialog.findChild(QTableWidget, "UixDetailTable").rowCount() == 12
    assert dialog.requested_scene_id is None
    assert not dialog.live_dispatch_enabled

    source.setCurrentIndex(source.findData("local"))
    new_filter = dialog.findChild(QComboBox, "UixReadinessFilter")
    assert new_filter.currentData() is None
    assert dialog.findChild(QTableWidget, "UixDetailTable").rowCount() == 3
    dialog.close()


def test_main_window_returns_to_exact_selected_scene_without_persistence(qtbot) -> None:
    workspace = _workspace_with_mixed_real_scenes()
    original = repr(workspace)
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    window.open_credit_uix_preview()

    preview = window._active_uix_preview
    assert preview is not None
    assert window.fixture_code == "REAL_UIX22_PREVIEW"
    assert preview._app_shell is True
    assert window._content_layout.itemAt(0).widget() is preview

    selector = preview.findChild(QComboBox, "UixDataSourceSelector")
    assert selector is not None
    selector.setCurrentIndex(selector.findData("local"))
    assert preview._using_local_inputs()
    table = preview.findChild(QTableWidget, "UixDetailTable")
    assert table is not None
    table.setCurrentCell(2, 0)
    open_scene = preview.findChild(QPushButton, "UixOpenSceneInWorkspace")
    assert open_scene is not None and open_scene.isEnabled()
    open_scene.click()

    assert window._active_uix_preview is None
    assert window.fixture_code == "REAL_WORKSPACE"
    assert window._selected_scene_id == "SCENE_003"
    table = next(
        t for t in window.findChildren(QTableWidget) if t.columnCount() == 9 and t.rowCount() == 3
    )
    assert table.item(table.currentRow(), 0).text() == "S003"
    assert window.current_workspace == workspace
    assert repr(workspace) == original
    window.close()


def test_new_uix_entry_starts_with_distinct_demo_states_then_allows_local_scan(qtbot) -> None:
    workspace = _workspace_with_mixed_real_scenes()
    dialog = CreditUixDialog(workspace=workspace, initial_state="UIX-05-C", default_to_demo=True)
    qtbot.addWidget(dialog)
    selector = dialog.findChild(QComboBox, "UixDataSourceSelector")
    assert selector is not None
    assert selector.currentData() == "demo"
    rows = dialog.findChild(QTableWidget, "UixDetailTable")
    assert rows.rowCount() == 2
    assert rows.item(0, 2).text() == "SUBMIT_UNCERTAIN"
    assert dialog._report_payload()["mode"] == "OFFLINE_SIMULATION"

    selector.setCurrentIndex(selector.findData("local"))
    local = dialog.findChild(QTableWidget, "UixDetailTable")
    assert local.rowCount() == 3
    assert local.item(0, 0).text() == "SCENE_001"
    assert dialog._report_payload()["mode"] == "LOCAL_SCENE_READINESS_REPORT"
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_uix_screen_paging_has_safe_edges_and_no_live_action(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-01-A")
    qtbot.addWidget(dialog)
    prev = dialog.findChild(QPushButton, "UixPreviousState")
    following = dialog.findChild(QPushButton, "UixNextState")
    assert prev is not None and following is not None
    assert not prev.isEnabled()
    following.click()
    assert dialog.current_state == "UIX-01-B"
    prev.click()
    assert dialog.current_state == "UIX-01-A"
    dialog.set_state("UIX-09-B")
    assert not following.isEnabled()
    prev.click()
    assert dialog.current_state == "UIX-09-A"
    assert dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled() is False
    assert dialog.minimumHeight() <= 700
    dialog.close()


def test_approved_dialog_scenarios_keep_centered_native_modal_surface(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-08-B")
    qtbot.addWidget(dialog)
    for code in ("UIX-02-A", "UIX-04-A", "UIX-07-B", "UIX-08-A", "UIX-08-B"):
        dialog.set_state(code)
        root = dialog.scroller.widget()
        assert root is not None
        modal = root.findChild(QFrame, "UixScenarioModal")
        assert modal is not None
        assert modal.maximumWidth() == 1120
        assert 680 <= modal.minimumWidth() <= 1120
        assert root.findChild(QTableWidget, "UixDetailTable") is not None
        if code in {"UIX-08-A", "UIX-08-B"}:
            details = root.findChild(QFrame, "UixScenarioSidePanel")
            assert details is not None
            assert "Dampak" in " ".join(label.text() for label in details.findChildren(QLabel))
        assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.set_state("UIX-05-C")
    root = dialog.scroller.widget()
    assert root is not None
    assert root.findChild(QFrame, "UixScenarioModal") is None
    dialog.close()


def test_smart_plan_uses_two_columns_of_approved_synthetic_information(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-A")
    qtbot.addWidget(dialog)
    side = dialog.findChild(QFrame, "UixScenarioSidePanel")
    assert side is not None
    text = " ".join(label.text() for label in side.findChildren(QLabel))
    assert "Distribusi per Profil" in text
    assert "Profil A" in text
    assert "Data simulasi" in text
    assert dialog.findChild(QTableWidget, "UixDetailTable").rowCount() > 0
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_approved_credit_states_are_right_aligned_readonly_drawers(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-03-A")
    qtbot.addWidget(dialog)
    for state in ("UIX-03-A", "UIX-03-B"):
        dialog.set_state(state)
        drawer = dialog.scroller.widget().findChild(QFrame, "UixCreditDrawer")
        assert drawer is not None
        assert drawer.maximumWidth() == 650
        assert dialog.findChild(QTableWidget, "UixDetailTable") is not None
        assert not dialog.live_dispatch_enabled
    dialog.set_state("UIX-02-A")
    assert dialog.scroller.widget().findChild(QFrame, "UixCreditDrawer") is None
    dialog.close()


def test_final_approved_mockup_summary_metrics_and_profile_bars(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-A")
    qtbot.addWidget(dialog)
    assert [(label, value) for label, value, _note, _kind in dialog._metrics_for("UIX-02-A")] == [
        ("Scene Diperiksa", "12 dari 60"),
        ("Siap Dialokasikan", "10 scene"),
        ("Perlu Perhatian", "2 scene"),
        ("Total Estimasi", "105 kredit*"),
    ]
    bars = dialog.findChildren(QProgressBar, "UixExampleCreditBar")
    assert sorted((bar.value(), bar.maximum()) for bar in bars) == [
        (21, 45),
        (42, 55),
        (42, 65),
    ]
    assert not dialog.live_dispatch_enabled

    assert [(label, value) for label, value, _note, _kind in dialog._metrics_for("UIX-08-A")] == [
        ("Total Proyek", "60 scene"),
        ("Sudah Diperiksa", "12 dari 60"),
        ("Input Siap", "10 scene"),
        ("Butuh Perbaikan", "2 scene"),
    ]
    dialog.set_state("UIX-08-B")
    assert [(label, value) for label, value, _note, _kind in dialog._metrics_for("UIX-08-B")] == [
        ("Kebijakan", "BELUM DIVERIFIKASI"),
        ("Profil Contoh", "3 PROFIL"),
        ("Generate Live", "DINONAKTIFKAN"),
        ("Scene Diperiksa", "12 DARI 60"),
    ]
    assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.close()


def test_main_app_preview_reuses_real_navigation_instead_of_duplicate_fake_shell(
    qtbot,
) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_credit_uix_preview()
    preview = window._active_uix_preview
    assert preview is not None
    assert preview._app_shell is True
    assert window.fixture_code == "REAL_UIX22_PREVIEW"
    assert window._content_layout.itemAt(0).widget() is preview
    assert preview.minimumWidth() == 640
    assert preview.findChild(QFrame, "UixSidebar").isHidden()
    assert preview.findChild(QFrame, "UixRightDock").isHidden()
    assert preview.current_state == "UIX-01-A"
    assert preview.source_selector.currentData() == "demo"
    assert preview.live_dispatch_enabled is False
    assert window._connection_badge.text().endswith("Mode Lokal")

    # A double-click cannot stack a second parallel UIX window.
    window.open_credit_uix_preview()
    assert window._active_uix_preview is preview

    back = preview.findChild(QPushButton, "UixClosePreview")
    assert back is not None and "Kembali" in back.text()
    back.click()
    assert window._active_uix_preview is None
    assert window.fixture_code == "UI-IMG-001A"
    window.close()


def test_navigation_away_from_embedded_uix_cleans_up_active_page(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_credit_uix_preview()
    assert window._active_uix_preview is not None
    window.show_fixture("UI-IMG-002A")
    assert window.fixture_code == "UI-IMG-002A"
    assert window._active_uix_preview is None
    assert window._uix_return_workspace is None
    window.close()


def test_standalone_uix_preview_retains_seven_readonly_routes(qtbot) -> None:
    dialog = CreditUixDialog()
    qtbot.addWidget(dialog)
    sidebar = dialog.findChild(QFrame, "UixSidebar")
    dock = dialog.findChild(QFrame, "UixRightDock")
    assert sidebar is not None and not sidebar.isHidden()
    assert dock is not None and not dock.isHidden()
    assert dialog._app_shell is False
    dialog.close()


def test_tariff_and_policy_final_panels_use_owner_approved_readonly_rows(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-08-B")
    qtbot.addWidget(dialog)

    panel = dialog.findChild(QFrame, "UixApprovedPolicyDetail")
    assert panel is not None
    values = " ".join(label.text() for label in panel.findChildren(QLabel))
    assert "Pemeriksaan Kebijakan" in values
    assert "Multi-akun bersamaan" in values
    assert "Bukti & tanggal peninjauan" in values
    assert "BELUM DIVERIFIKASI" in values
    assert "Status UNKNOWN" in values
    assert dialog.findChild(QTableWidget, "UixDetailTable").isHidden()
    assert not dialog.live_dispatch_enabled

    dialog.set_state("UIX-08-A")
    tariff = dialog.findChild(QFrame, "UixApprovedTariffDetail")
    assert tariff is not None
    text = " ".join(label.text() for label in tariff.findChildren(QLabel))
    assert "Versi tarif & sumber data" in text
    assert "vDEMO-1" in text and "vDEMO-2" in text
    assert "Kedaluwarsa" in text
    assert "Model tetap" in text
    assert dialog.findChild(QTableWidget, "UixDetailTable").isHidden()
    assert dialog.findChild(QFrame, "UixScenarioSidePanel") is not None
    assert not dialog.findChild(QPushButton, "UixLiveGenerate").isEnabled()
    dialog.close()


def test_owner_approved_smart_plan_stepper_and_policy_alert_colors(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-02-A")
    qtbot.addWidget(dialog)
    progress = dialog.findChild(QFrame, "UixSmartCreditPlanStepper")
    assert progress is not None
    stages = progress.findChildren(QLabel, "UixSmartCreditPlanStage")
    assert [stage.text() for stage in stages] == [
        "1. Scan selesai",
        "2. Bagi scene",
        "3. Tinjau anggaran",
    ]
    dialog.set_state("UIX-08-A")
    labels = [label.text() for label in dialog.scroller.widget().findChildren(QLabel)]
    assert "Persetujuan rencana v3 sudah kedaluwarsa" in labels
    dialog.set_state("UIX-08-B")
    labels = [label.text() for label in dialog.scroller.widget().findChildren(QLabel)]
    assert "G1 — Izin otomatisasi belum dapat dipastikan" in labels
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_modal_groups_show_real_qt_scrim_over_readonly_workspace_and_agent(qtbot) -> None:
    dialog = CreditUixDialog(initial_state="UIX-08-B", default_to_demo=True)
    qtbot.addWidget(dialog)
    for state in (
        "UIX-02-A",
        "UIX-04-A",
        "UIX-07-A",
        "UIX-08-A",
        "UIX-08-B",
    ):
        dialog.set_state(state)
        root = dialog.scroller.widget()
        assert root is not None
        layered = root.layout()
        assert isinstance(layered, QStackedLayout)
        assert layered.stackingMode() == QStackedLayout.StackingMode.StackAll
        assert layered.count() == 2
        assert root.findChild(QFrame, "UixModalScrim") is not None
        assert root.findChild(QWidget, "UixWorkspaceBackdrop") is not None
        agent = root.findChild(QFrame, "UixBackdropAgentDock")
        assert agent is not None
        assert agent.width() <= 280
        assert root.findChild(QTableWidget, "UixBackdropSceneTable") is not None
        assert root.findChild(QFrame, "UixScenarioModal") is not None
        assert dialog.live_dispatch_enabled is False

    dialog.set_state("UIX-01-A")
    root = dialog.scroller.widget()
    assert root is not None
    assert isinstance(root.layout(), QVBoxLayout)
    assert root.findChild(QFrame, "UixModalScrim") is None
    dialog.close()


def test_policy_overlay_backdrop_uses_local_workspace_without_remote_entitlement(qtbot) -> None:
    workspace = _workspace_with_mixed_real_scenes()
    dialog = CreditUixDialog(workspace=workspace, initial_state="UIX-08-B", default_to_demo=True)
    qtbot.addWidget(dialog)
    root = dialog.scroller.widget()
    assert root is not None
    backdrop = root.findChild(QWidget, "UixWorkspaceBackdrop")
    assert backdrop is not None
    text = " ".join(label.text() for label in backdrop.findChildren(QLabel))
    assert workspace.episode_id in text
    assert "Workspace lokal" in text
    assert "TIDAK DIKETAHUI" in text
    assert "PROVIDER TIDAK TERSAMBUNG" in text
    assert not dialog.live_dispatch_enabled
    dialog.close()
