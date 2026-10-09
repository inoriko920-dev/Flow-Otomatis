"""Read-only production settings over the owner-approved STEP 09 layout.

Values must describe the current local process/workspace, not sample projects
or assumed Google Flow availability. This screen never changes provider state.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen
from flow_otomatis.presentation.widgets import info_banner, muted_label, secondary_button


@dataclass(frozen=True, slots=True)
class LocalSettingsSnapshot:
    """Safe observable local state, never an assertion of remote entitlement."""

    active_workspace_model: str | None
    active_workspace_resolution: str | None
    active_workspace_aspect_ratio: str | None
    active_workspace_scene_count: int | None


def _replace_labeled_value(root: QWidget, key: str, new_value: str) -> None:
    for label in root.findChildren(QLabel):
        if label.text() != key:
            continue
        parent = label.parentWidget()
        if parent is None:
            continue
        row_labels = parent.findChildren(QLabel, options=Qt.FindChildOption.FindDirectChildrenOnly)
        if len(row_labels) == 2 and row_labels[0] is label:
            row_labels[1].setText(new_value)
            row_labels[1].setWordWrap(True)
            return
    raise RuntimeError(f"Approved settings layout lacks field: {key}")


def build_local_settings_view(
    snapshot: LocalSettingsSnapshot, *, on_refresh: Callable[[], object]
) -> QWidget:
    """Bind the real current local Workspace to the frozen settings composition."""

    root = build_screen(get_fixture("UI-IMG-007A"))
    root.setObjectName("RealLocalSettings")
    layout = root.layout()
    if not isinstance(layout, QVBoxLayout):
        raise RuntimeError("Approved settings view has no vertical layout")

    layout.insertWidget(
        1,
        info_banner(
            "PENGATURAN TERKUNCI • KONFIGURASI LOKAL",
            "Nilai di bawah adalah target workflow atau data Workspace yang sedang "
            "dibuka, bukan pilihan model yang telah diverifikasi di Google Flow. "
            "Tidak ada opsi provider atau kredit yang dapat diubah dari layar ini.",
            "info",
        ),
    )
    if snapshot.active_workspace_model is None:
        model = "Omni Flash 1.1 • target workflow (belum ada project aktif)"
        resolution = "720p • target workflow"
        aspect = "16:9 • target workflow"
    else:
        model = f"{snapshot.active_workspace_model} • dari Workspace lokal"
        resolution = f"{snapshot.active_workspace_resolution} • dari Workspace lokal"
        aspect = f"{snapshot.active_workspace_aspect_ratio} • dari Workspace lokal"
    _replace_labeled_value(root, "Model", model)
    _replace_labeled_value(root, "Resolusi", resolution)
    _replace_labeled_value(root, "Rasio Aspek", aspect)
    _replace_labeled_value(root, "Bahasa", "Bahasa Indonesia • tampilan aplikasi")
    _replace_labeled_value(root, "Queue R1", "Kontrak serial • 1 worker • live tidak aktif")
    _replace_labeled_value(root, "Autosave", "Penyimpanan lokal pada aksi • bukan cloud sync")
    _replace_labeled_value(root, "Provider berbayar", "Generate live belum diaktifkan")

    card = QWidget()
    card.setObjectName("RealSettingsFooter")
    actions = QVBoxLayout(card)
    actions.setContentsMargins(0, 6, 0, 6)
    count = (
        f"{snapshot.active_workspace_scene_count} Scene"
        if snapshot.active_workspace_scene_count is not None
        else "Belum ada Workspace terbuka"
    )
    actions.addWidget(muted_label(f"Workspace saat ini: {count}"))
    refresh = secondary_button("Muat Ulang Status Lokal")
    refresh.setObjectName("RealSettingsRefresh")
    refresh.clicked.connect(on_refresh)
    actions.addWidget(refresh)
    layout.insertWidget(layout.count() - 1, card)
    return root
