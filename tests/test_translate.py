import json
import os

import pytest
import requests
import vcr
from i18ntools.parse_i18n_file import parse_i18n_file
from i18ntools.translate import get_default_filepath, make_api_call, translate_file

# Do not record any authorization headers
filter_headers = ["authorization", "Ocp-Apim-Subscription-Key"]


@pytest.fixture
def fake_german_translations():
    """Fixture that returns static German translation data."""
    with open("tests/resources/example_de.json") as f:
        return json.load(f)


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
    # Set the environment variable and then unset it it.
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    os.environ.pop("TRANSLATOR_API_SUBSCRIPTION_KEY")
    with pytest.raises(KeyError):
        translate_file("tests/resources/example.properties", "de")


@vcr.use_cassette("tests/cassettes/test_translate_with_invalid_api_key.yml")
def test_translate_with_invalid_api_key():
    """HTTPError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is set to invalid key
    """
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    with pytest.raises(requests.exceptions.HTTPError):
        translate_file("tests/resources/example.properties", "de")


@vcr.use_cassette(
    "tests/cassettes/test_make_api_call.yml", filter_headers=filter_headers
)
def test_make_api_call(fake_german_translations):
    """make_api_call returns JSON when the API call is successful"""
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    input_data = parse_i18n_file("tests/resources/example.properties")
    translation_info = make_api_call(input_data, "de")
    assert translation_info == fake_german_translations
