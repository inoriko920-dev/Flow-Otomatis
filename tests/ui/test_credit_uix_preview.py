"""Validate all approved E12-02 UIX states without any live Google service."""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton, QTableWidget

from flow_otomatis.presentation.credit_uix_preview import (
    SCENARIO_BY_ID,
    UIX_SCENARIOS,
    CreditUixDialog,
)


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
