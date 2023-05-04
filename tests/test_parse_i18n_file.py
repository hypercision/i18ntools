import pytest
from i18ntools.parse_i18n_file import parse_i18n_file


def test_parse_file():
    parsed_data = parse_i18n_file("tests/example.properties")
    assert len(parsed_data.keys()) == 6
    assert (
        parsed_data["instructorService.removeSession.success"] == "{0} session removed."
    )
    assert parsed_data["default.invalid.min.message"] == (
        "Property [{0}] of class [{1}] with value "
        "[{2}] is less than minimum value [{3}]"
    )

    assert parsed_data[
        "instructor.submitWithCustomTime.customSubmitTS.missing.error"
    ] == (
        "The customSubmitTS parameter is missing. \\"
        "\n    It must be present and of type Date."
    )

    assert parsed_data["TheBeths.YourSide.lyrics"] == (
        "I want to see you knocking at the door. \\"
        "\n    I wanna leave you out there waiting in the downpour. \\"
        "\n    Singing that you’re sorry, dripping on the hall floor."
    )


def test_parse_file_with_duplicate_keys():
    """SyntaxWarning is raised for files with duplicate keys"""
    with pytest.raises(SyntaxWarning):
        parse_i18n_file("tests/duplicate.properties")
