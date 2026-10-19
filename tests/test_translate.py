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


@pytest.fixture
def fake_portuguese_i18n_data():
    """Fixture that returns static Portuguese i18n file data."""
    # Open the input file in read mode to read its contents
    with open(
        "tests/resources/translations2_pt.properties", "r", encoding="utf-8"
    ) as f:
        return f.read()


@pytest.mark.parametrize(
    ("input_file_path", "output_lang", "expected"),
    [
        ("../tmp/messages.properties", "zh", "../tmp/messages_zh.properties"),
        ("/home/docs/i18n_vi.properties", "es", "/home/docs/i18n_es.properties"),
        ("/home/docs/i18n_en_GB.properties", "de", "/home/docs/i18n_de.properties"),
        # Regression: underscore in a directory name
        (
            "webapp/i18n_main/messageBundle.properties",
            "en",
            "webapp/i18n_main/messageBundle_en.properties",
        ),
        (
            "webapp/i18n_main/messageBundle_fr.properties",
            "en",
            "webapp/i18n_main/messageBundle_en.properties",
        ),
        # Underscores in multiple directories and in the filename
        (
            "my_project/src_main/app_messages_en.properties",
            "de",
            "my_project/src_main/app_messages_de.properties",
        ),
        # Underscore in the filename that is not a locale
        ("message_bundle.properties", "de", "message_bundle_de.properties"),
        # Script and numeric region locale suffixes
        ("messages_zh_Hant_TW.properties", "fr", "messages_fr.properties"),
        ("messages_zh_Hant.properties", "fr", "messages_fr.properties"),
        ("messages_es_419.properties", "pt", "messages_pt.properties"),
        # Three-letter language code
        ("messages_fil.properties", "de", "messages_de.properties"),
        # No directory
        ("messages.properties", "de", "messages_de.properties"),
        # Dots and underscores in directory names
        (
            "my.app_v2/i18n_files/messages.properties",
            "de",
            "my.app_v2/i18n_files/messages_de.properties",
        ),
        # No file extension
        ("i18n_dir/messages_en", "de", "i18n_dir/messages_de"),
        # Windows-style path separators are preserved
        (
            "C:\\web_app\\i18n_main\\messages_en.properties",
            "de",
            "C:\\web_app\\i18n_main\\messages_de.properties",
        ),
    ],
)
def test_get_default_filepath(input_file_path, output_lang, expected):
    assert get_default_filepath(input_file_path, output_lang) == expected


def test_get_default_filepath_accepts_path_objects(tmp_path):
    """A pathlib.Path input produces the same result as its string form."""
    input_path = tmp_path / "i18n_main" / "messages_en.properties"
    expected = str(tmp_path / "i18n_main" / "messages_de.properties")
    assert get_default_filepath(input_path, "de") == expected


def test_translate_without_api_key():
    """KeyError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is not set
    """
    # Set the environment variable and then unset it.
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    os.environ.pop("TRANSLATOR_API_SUBSCRIPTION_KEY")
    with pytest.raises(KeyError):
        translate_file("tests/resources/example.properties", "de")


@vcr.use_cassette(
    "tests/cassettes/test_translate_with_invalid_api_key.yml"
)  # type: ignore
def test_translate_with_invalid_api_key():
    """HTTPError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is set to an invalid key
    """
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    with pytest.raises(requests.exceptions.HTTPError):
        translate_file("tests/resources/example.properties", "de")


@vcr.use_cassette(
    "tests/cassettes/test_translate_file.yml", filter_headers=filter_headers
)  # type: ignore
def test_translate_file(tmp_path, fake_portuguese_i18n_data):
    """translate_file successfully writes translations to an output file"""
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    output_file = tmp_path / "example2_pt.properties"
    translate_file(
        "tests/resources/example2.properties", "pt", output_file_path=output_file
    )
    assert output_file.read_text() == fake_portuguese_i18n_data


@vcr.use_cassette(
    "tests/cassettes/test_translate_file_without_backslashes.yml",
    filter_headers=filter_headers,
)  # type: ignore
def test_translate_file_without_backslashes(
    tmp_path, fake_german_i18n_data_without_backslashes
):
    """translate_file successfully writes translations to an output file"""
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    output_file = tmp_path / "example_de.properties"
    translate_file(
        "tests/resources/example.properties",
        "de",
        remove_backslashes=True,
        output_file_path=output_file,
    )
    assert output_file.read_text() == fake_german_i18n_data_without_backslashes


@vcr.use_cassette(
    "tests/cassettes/test_make_api_call.yml", filter_headers=filter_headers
)  # type: ignore
def test_make_api_call(fake_german_translations):
    """make_api_call returns JSON when the API call is successful"""
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    input_data = parse_i18n_file("tests/resources/example.properties")
    translation_info = make_api_call(input_data, "de")
    assert translation_info == fake_german_translations
