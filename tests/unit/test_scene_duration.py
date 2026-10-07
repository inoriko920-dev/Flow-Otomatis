import pytest

from flow_otomatis.domain.errors import InvalidDurationError
from flow_otomatis.domain.scene import recommend_flow_duration


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        (3.81, 4),
        (4.00, 4),
        (4.01, 6),
        (6.00, 6),
        (6.01, 8),
        (7.32, 8),
        (8.00, 8),
        (8.01, 10),
        (10.00, 10),
    ],
)
def test_recommend_flow_duration_boundary_rules(target: float, expected: int) -> None:
    assert recommend_flow_duration(target) == expected


def test_recommend_flow_duration_rejects_over_ten_seconds() -> None:
    with pytest.raises(InvalidDurationError):
        recommend_flow_duration(10.01)
