import os

import pytest
import requests
import vcr
from i18ntools.translate_missing import translate_missing_messages

# Do not record any authorization headers
filter_headers = ["authorization", "Ocp-Apim-Subscription-Key"]


@pytest.fixture
def fake_german_i18n_data():
    """Fixture that returns static German i18n file data."""
    # Open the input file in read mode to read its contents
    with open("tests/resources/translations_de.properties", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def fake_german_i18n_data_unsorted():
    """Fixture that returns static German i18n file data without
    comments or newlines between translations.
    """
    # Open the input file in read mode to read its contents
    with open(
        "tests/resources/translations_de2.properties", "r", encoding="utf-8"
    ) as f:
        return f.read()


def test_translate_missing_messages_without_input_file(tmp_path):
    """FileNotFoundError is raised when the input file specified
    does not exist.
    """
    with pytest.raises(FileNotFoundError):
        translate_missing_messages("messages.properties", "ms")


def test_translate_missing_messages_without_output_file(tmp_path):
    """FileNotFoundError is raised when the output file specified
    does not exist.
    """
    with pytest.raises(FileNotFoundError):
        translate_missing_messages("tests/resources/example.properties", "de")


def test_translate_missing_messages_without_api_key(tmp_path):
    """KeyError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is not set
    """
    # Set the environment variable and then unset it it.
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    os.environ.pop("TRANSLATOR_API_SUBSCRIPTION_KEY")
    output_file = tmp_path / "messages_de.properties"
    output_file.write_text(
        "default.invalid.min.message=Eigenschaft [{0}] der Klasse [{1}] "
        "mit dem Wert [{2}] ist kleiner als der Mindestwert [{3}]"
    )
    with pytest.raises(KeyError):
        translate_missing_messages(
            "tests/resources/example.properties",
            "de",
            sort_file=False,
            output_file_path=str(output_file),
        )


@vcr.use_cassette(
    "tests/cassettes/test_translate_missing_messages_with_invalid_api_key.yml"
)  # type: ignore
def test_translate_missing_messages_with_invalid_api_key(tmp_path):
    """HTTPError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is set to invalid key
    """
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "three_little_ducks"
    output_file = tmp_path / "messages_de.properties"
    output_file.write_text(
        "default.invalid.min.message=Die Eigenschaft [{0}] der Klasse [{1}] "
        "mit dem Wert [{2}] ist kleiner als der Mindestwert [{3}]\n"
    )
    with pytest.raises(requests.exceptions.HTTPError):
        translate_missing_messages(
            "tests/resources/example.properties",
            "de",
            sort_file=False,
            output_file_path=str(output_file),
        )


@vcr.use_cassette(
    "tests/cassettes/test_translate_missing_messages.yml", filter_headers=filter_headers
)  # type: ignore
def test_translate_missing_messages(tmp_path, fake_german_i18n_data):
    """translate_missing_messages fills an i18n file with the
    translations it was missing
    """
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    output_file = tmp_path / "messages_de.properties"
    output_file.write_text(
        "default.invalid.min.message=Die Eigenschaft [{0}] der Klasse [{1}] "
        "mit dem Wert [{2}] ist kleiner als der Mindestwert [{3}]\n"
    )
    translate_missing_messages(
        "tests/resources/example.properties",
        "de",
        sort_file=True,
        output_file_path=str(output_file),
    )
    assert output_file.read_text() == fake_german_i18n_data


@vcr.use_cassette(
    "tests/cassettes/test_translate_missing_messages_without_sorting.yml",
    filter_headers=filter_headers,
)  # type: ignore
def test_translate_missing_messages_without_sorting(
    tmp_path, fake_german_i18n_data_unsorted
):
    """translate_missing_messages fills an i18n file with the
    translations it was missing, but does not copy over comments
    from the source file because it was called with sort_file=False
    """
    os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"] = "not-an-actual-api-key"
    output_file = tmp_path / "messages_de.properties"
    output_file.write_text(
        "default.invalid.min.message=Die Eigenschaft [{0}] der Klasse [{1}] "
        "mit dem Wert [{2}] ist kleiner als der Mindestwert [{3}]\n"
    )
    translate_missing_messages(
        "tests/resources/example.properties",
        "de",
        sort_file=False,
        output_file_path=str(output_file),
    )
    assert output_file.read_text() == fake_german_i18n_data_unsorted
