import pytest
from i18ntools.translate import get_default_filepath, translate_file


def test_get_default_filepath():
    assert (
        get_default_filepath("../tmp/messages.properties", "zh")
        == "../tmp/messages_zh.properties"
    )

    assert (
        get_default_filepath("/home/docs/i18n_vi.properties", "es")
        == "/home/docs/i18n_es.properties"
    )

    assert (
        get_default_filepath("/home/docs/i18n_en_GB.properties", "de")
        == "/home/docs/i18n_de.properties"
    )


def test_translate_without_api_key():
    """KeyError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is not set
    """
    with pytest.raises(KeyError):
        translate_file("tests/example.properties", "de")
