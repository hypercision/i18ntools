#!/usr/bin/env python
"""Parses an i18n Java properties file and returns the data as a dictionary.

The benefit of this method over using configparser is that the whitespace in
multiline values is preserved.

Note that this method does not work properly for multiline translations
with an "=" character in them.

See related question: https://stackoverflow.com/questions/76047202
"""

import argparse
from pathlib import Path


def parse_i18n_file(file_path):
    """Parses an i18n Java properties file and returns the data as a dictionary.

    Note that this method does not work properly for multiline translations
    with an "=" character in them.

    Keyword arguments:
    file_path -- filepath of the i18n Java properties file to parse
    """
    if not Path(file_path).exists():
        raise FileNotFoundError("File {0} does not exist".format(file_path), file_path)

    # Open the input file in read mode to read its contents
    with open(file_path, "r", encoding="utf-8") as f:
        file_contents = f.readlines()

    data = {}
    duplicate_keys = set()
    mostRecentKey = None
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
            data[mostRecentKey] += "\n" + line.rstrip()
            continue

        key = parts[0]
        value = parts[1]
        if key in data:
            duplicate_keys.add(key)
        data[key] = value
        mostRecentKey = key

    if len(duplicate_keys) > 0:
        raise SyntaxWarning(
            f"{file_path} cannot be parsed for translation. "
            f"It has at least one duplicate key: {duplicate_keys}"
        )

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
    args = parser.parse_args()
    result = parse_i18n_file(args.input_file)
    for key, value in result.items():
        print("key", key)
        print("value", value)


if __name__ == "__main__":
    main()
