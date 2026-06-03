from app.data_store import get_value, load_data


def test_load_data_returns_dict_with_expected_keys() -> None:
    data = load_data()
    assert isinstance(data, dict)
    assert data["hello"] == "world"
    assert data["app_name"] == "python-service"


def test_get_value_existing_key() -> None:
    assert get_value("hello") == "world"


def test_get_value_missing_key() -> None:
    assert get_value("__nonexistent_key__") is None
