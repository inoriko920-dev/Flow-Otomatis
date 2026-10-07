from pathlib import Path

from scripts.check_architecture import check_repository


def test_repository_passes_architecture_check() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    assert check_repository(repo_root) == []
