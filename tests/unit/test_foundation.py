from flow_otomatis import __version__
from flow_otomatis.bootstrap.main import main


def test_version_is_foundation_version() -> None:
    assert __version__ == "0.0.0"


def test_foundation_bootstrap_is_side_effect_light() -> None:
    assert main() == 0
