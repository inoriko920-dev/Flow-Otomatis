from pathlib import Path

from flow_otomatis.infrastructure.filesystem import PathService


def test_user_data_root_prefers_local_app_data() -> None:
    paths = PathService.discover(
        executable=Path("X:/portable/Flow-Otomatis.exe"),
        environ={"LOCALAPPDATA": "X:/Users/Test/AppData/Local"},
        home=Path("X:/Users/Test"),
    )

    assert paths.user_data_root.name == "Flow-Otomatis"
    assert paths.session_root.name == "Sessions"
    assert paths.log_root.name == "Logs"


def test_discovery_does_not_use_current_working_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    paths = PathService.discover(
        environ={},
        home=tmp_path / "home",
    )

    assert paths.user_data_root == (tmp_path / "home/AppData/Local/Flow-Otomatis").resolve()
    assert paths.app_root != tmp_path
