import pytest
from i18ntools.parse_i18n_file import parse_i18n_file


def test_parse_file():
    parsed_data = parse_i18n_file("tests/resources/example.properties")
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


def test_parse_file_2():
    """Test for parsing a file with a value that has two consecutive
    apostraphes characters: '
    """
    parsed_data = parse_i18n_file("tests/resources/example2.properties")
    assert len(parsed_data.keys()) == 3
    assert parsed_data["handshake.register.mobileDeviceLimitReached.error"] == (
        "The device limit of {0} devices has been reached \\"
        "\n    for your company''s account and new devices cannot use the "
        "application. Please contact your \\"
        "\n    administrator."
    )
    assert parsed_data["recordAttendance.segment.notFound.error"] == (
        "Segment with segmentID {0} \\" "\n    not found in the SessionItem's segments"
    )
    assert parsed_data["me"] == "first!"


def test_parse_file_with_duplicate_keys():
    """SyntaxWarning is raised for files with duplicate keys"""
    with pytest.raises(SyntaxWarning):
        parse_i18n_file("tests/resources/duplicate.properties")
