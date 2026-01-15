#!/usr/bin/env python
"""Parses an i18n Java properties file and returns the data as a dictionary.

If called with remove_backslashes=False, then the whitespace in
multiline values is preserved.

If called with remove_backslashes=True, then configparser is used
and the whitespace and backslashes in multiline values are removed.

Note that this method does not work properly for multiline translations
with an "=" character in them.
"""

import argparse
import configparser
import tempfile
from pathlib import Path


def parse_i18n_file(file_path, remove_backslashes=False):
    """Parses an i18n Java properties file and returns the data as a dictionary.

    Note that this method does not work properly for multiline translations
    with an "=" character in them.

    Keyword arguments:
    file_path -- filepath of the i18n Java properties file to parse
    remove_backslashes -- when true, the data returned will not have the
        backslashes used in multiline values.
        Multiline values will be transformed into single line values.
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File {file_path} does not exist")

    # Open the input file in read mode to read its contents
    with open(file_path, "r", encoding="utf-8") as f:
        file_contents = f.readlines()

    data = {}
    duplicate_keys = set()
    most_recent_key = None
    for line in file_contents:
        # Skip comments and empty lines
        if line.startswith("#") or line.strip() == "":
            continue

        # Extract the key and value on this line
        parts = line.strip().split("=", 1)
        if len(parts) == 1:
            # This line is part of a multiline value.
            # Add the additional line to the value in our dictionary,
            # stripping the trailing whitespace.
            data[most_recent_key] += "\n" + line.rstrip()
            continue

        key = parts[0]
        value = parts[1]
        if key in data:
            duplicate_keys.add(key)
        data[key] = value
        most_recent_key = key

    if len(duplicate_keys) > 0:
        raise SyntaxWarning(
            f"{file_path} cannot be parsed for translation. "
            f"It has at least one duplicate key: {duplicate_keys}"
        )

    if remove_backslashes:
        # Now that we've ensured the file has no duplicate properties, return
        # the data as a dictionary with multiline values transformed into
        # single line values.
        return parse_i18n_file_without_backslashes(file_path)

    return data


def convert_properties_to_ini(input_path, ini_path):
    """Reads a properties file and writes it as an .ini file with a [DEFAULT] section
    header to make it compatible with configparser.

    Keyword arguments:
    input_path -- filepath of the i18n Java properties file to convert
    ini_path -- filepath of the output .ini file
    """
    with (
        open(input_path, "r", encoding="utf-8") as infile,
        open(ini_path, "w", encoding="utf-8") as outfile,
    ):
        # Add a dummy section header
        outfile.write("[DEFAULT]\n")
        outfile.writelines(infile.readlines())


def merge_multiline_string(multiline_string: str) -> str:
    """Takes a multiline string as input, removes the backslashes at the
    end of each line, and returns a single line string.

    Keyword arguments:
    multiline_string -- the input string potentially containing multiple lines
            with backslash continuations.
    """
    # Split the string into lines and strip any leading/trailing whitespace
    # from each line
    lines = multiline_string.splitlines()
    # Remove the backslash from the end of each line
    processed_lines = [line.rstrip("\\").strip() for line in lines]
    # Join the lines into a single string, filtering out any empty lines
    # to avoid leading/trailing spaces
    merged_string = " ".join(line for line in processed_lines if line)
    return merged_string


def parse_i18n_file_without_backslashes(file_path):
    """Parses an i18n Java properties file and returns the data as a dictionary.
    Multiline values will be transformed into single line values with the
    backslashes removed.

    Note that this method does not work properly for multiline translations
    with an "=" character in them.

    Keyword arguments:
    file_path -- filepath of the i18n Java properties file to parse
    """
    # Use a temporary file that is automatically cleaned up
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ini", encoding="utf-8", delete=True
    ) as temp_ini:
        # Convert the properties file into a temporary .ini file
        convert_properties_to_ini(file_path, temp_ini.name)

        # Parse the temporary .ini file
        # Use RawConfigParser to avoid any interpolation or automatic conversions
        config = configparser.RawConfigParser(empty_lines_in_values=False)
        # Override the optionxform method to prevent lowercase conversion of the keys
        config.optionxform = str  # type: ignore

        config.read(temp_ini.name, encoding="utf-8")

    data = {}
    for key, value in config["DEFAULT"].items():
        merged_string = merge_multiline_string(value)
        data[key] = merged_string

    return data


def main():
    """Build a CLI for calling parse_i18n_file and printing the resulting dictionary.
    This is primarily for development/debugging purposes.
    """
    parser = argparse.ArgumentParser(
        description=("Parses an i18n Java properties file and prints its data")
    )
    parser.add_argument(
        "-i",
        "--input_file",
        required=True,
        type=str,
        help=(
            "filename of input i18n Java properties file. "
            "Can be specified as a relative or absolute file path."
        ),
    )
    parser.add_argument(
        "-r",
        "--remove_backslashes",
        action="store_true",
        help=(
            "the data returned will not have the "
            "backslashes used in multiline values."
        ),
    )
    args = parser.parse_args()
    result = parse_i18n_file(args.input_file, args.remove_backslashes)
    for key, value in result.items():
        print("key", key)
        print("value", value)


if __name__ == "__main__":
    main()
