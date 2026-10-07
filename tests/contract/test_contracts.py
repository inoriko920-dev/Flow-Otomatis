from flow_otomatis.contracts import CONTRACTS_SCHEMA_VERSION


def test_contract_schema_version_starts_at_one() -> None:
    assert CONTRACTS_SCHEMA_VERSION == 1
