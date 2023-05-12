from i18ntools.sort_i18n_file import sort_i18n_file


def test_sort_i18n_file(tmp_path):
    output_file = tmp_path / "output_de.properties"
    with open(output_file, "w") as f:
        f.write("handshake.register.suspended.error=ok\n")
        f.write("instructorService.removeSession.success=hello\n")
        f.write("handshake.register.disabledException.error=world\n")
        f.write("TheBeths.YourSide.lyrics=German Translation\n")

    output_lang = "de"
    # Sort the output file
    sort_i18n_file("tests/example.properties", output_lang, str(output_file))

    with output_file.open() as f:
        output_file_contents = f.readlines()
    # The file has 9 lines (excluding the final empty line)
    assert len(output_file_contents) == 9
    assert output_file_contents[1] == "# Track 4 on Expert In A Dying Field\n"
    assert output_file_contents[2] == "TheBeths.YourSide.lyrics=German Translation\n"
