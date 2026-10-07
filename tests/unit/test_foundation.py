from flow_otomatis import __version__
from flow_otomatis.bootstrap.main import build_main_window


def test_version_is_ui_implementation_version() -> None:
    assert __version__ == "0.1.0"


def test_bootstrap_builds_default_shell(qtbot: object) -> None:
    del qtbot
    window = build_main_window()
    try:
        assert window.windowTitle() == "Flow-Otomatis"
        assert window.fixture_code == "UI-IMG-001A"
    finally:
        window.close()
