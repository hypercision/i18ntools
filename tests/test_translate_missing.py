import pytest
from i18ntools.translate_missing import translate_missing_messages


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
        translate_missing_messages("tests/example.properties", "de")


def test_translate_missing_messages_without_api_key(tmp_path):
    """KeyError is raised when environment variable
    TRANSLATOR_API_SUBSCRIPTION_KEY is not set
    """
    output_file = tmp_path / "messages_de.properties"
    output_file.write_text(
        "default.invalid.min.message=Eigenschaft [{0}] der Klasse [{1}] "
        "mit dem Wert [{2}] ist kleiner als der Mindestwert [{3}]"
    )
    with pytest.raises(KeyError):
        translate_missing_messages(
            "tests/example.properties", "de", False, str(output_file)
        )
