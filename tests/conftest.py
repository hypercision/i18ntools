import pytest


@pytest.fixture
def fake_german_i18n_data_without_backslashes():
    """Fixture that returns static German i18n file data with newlines and
    backslashes not preserved when input file was translated."""
    with open(
        "tests/resources/translations_de_no_backslashes.properties",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()
