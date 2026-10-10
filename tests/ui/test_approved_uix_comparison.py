"""Reference comparison never trusts missing/modified UI artwork."""

from __future__ import annotations

import hashlib

import pytest
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QLabel

from flow_otomatis.presentation import approved_uix_assets as assets
from flow_otomatis.presentation.approved_uix_comparison import (
    ApprovedUixComparisonDialog,
)
from flow_otomatis.presentation.credit_uix_preview import CreditUixDialog


def _make_png(tmp_path):
    image = QImage(1920, 1080, QImage.Format.Format_RGB32)
    image.fill(QColor("#edf4ff"))
    path = tmp_path / "synthetic_reference.png"
    assert image.save(str(path))
    return path


def test_approved_reference_manifest_has_22_unique_approved_hashes() -> None:
    assert len(assets.APPROVED_IMAGES) == 22
    assert len(set(assets.APPROVED_IMAGES.values())) == 22
    for code, (filename, digest) in assets.APPROVED_IMAGES.items():
        assert code.startswith("UIX-")
        assert filename.endswith(".png")
        assert len(digest) == 64
    with pytest.raises(assets.ApprovedReferenceError, match="tidak dikenal"):
        assets.load_verified_reference("UIX-FAKE", supplied_directory=None)


def test_reference_validation_uses_exact_bytes_not_just_filename(
    qtbot, tmp_path, monkeypatch
) -> None:
    image = _make_png(tmp_path)
    approved_sha = hashlib.sha256(image.read_bytes()).hexdigest()
    monkeypatch.setitem(
        assets.APPROVED_IMAGES,
        "UIX-08-B",
        (image.name, approved_sha),
    )
    result = assets.load_verified_reference("UIX-08-B", supplied_directory=tmp_path)
    assert result == image
    original = image.read_bytes()

    screen = QPixmap(str(image))
    viewer = ApprovedUixComparisonDialog("UIX-08-B", result, screen)
    qtbot.addWidget(viewer)
    assert viewer.findChildren(QLabel, "UixComparisonImage")
    assert len(viewer.findChildren(QLabel, "UixComparisonImage")) == 2
    assert image.read_bytes() == original
    viewer.close()

    image.write_bytes(original + b"unapproved")
    with pytest.raises(assets.ApprovedReferenceError, match="SHA-256"):
        assets.load_verified_reference("UIX-08-B", supplied_directory=tmp_path)


def test_main_ui_has_comparison_action_without_enabling_live(qtbot) -> None:
    preview = CreditUixDialog(initial_state="UIX-08-B")
    qtbot.addWidget(preview)
    assert preview.compare_button.objectName() == "UixCompareApproved"
    assert preview.compare_button.isEnabled()
    assert not preview.live_dispatch_enabled
    preview.close()
