#!/usr/bin/env python
"""This script sorts the messages in the output i18n Java properties file
so that they are in the same order as the messages in the input
i18n Java properties file. The output properties file will be overwritten
with the updated, sorted contents.

Note that this does not work properly for multiline translations
with an "=" character in them.
"""

# TODO: figure out a way to preserve the comments in the output i18n file
#  since they could be different from the comments in the input file.
#  Right now this script delete comments in the output file that are not
#  present in the input file.

import argparse
from pathlib import Path

from i18ntools.parse_i18n_file import parse_i18n_file
from i18ntools.translate import get_default_filepath


def sort_i18n_file(input_file_path, output_lang, output_file_path=None):
    """Sorts the messages in the output i18n Java properties file
    so that they are in the same order as the messages in the input
    i18n Java properties file. The output properties file will be overwritten
    with the updated, sorted contents.

    Note that this method does not work properly for multiline translations
    with an "=" character in them.

    Keyword arguments:
    input_file_path -- filepath of the i18n Java properties file to reference
            for the sort order
    output_lang -- language of the output file to sort i.e. de for German
    output_file_path -- filepath of the i18n Java properties file to sort.
            If this is left as None, then it defaults to the input_file with
            the output language appended to it.
            For example, messages.properties would become messages_de.properties
    """
    if not Path(input_file_path).exists():
        raise FileNotFoundError(
            "File {0} does not exist".format(input_file_path), input_file_path
        )

    if output_file_path is None:
        # Make output_file_path be the input_file_path with the
        # output_lang appended to it. For example, "/dir/messages.properties"
        # would become "/dir/messages_de.properties".
        output_file_path = get_default_filepath(input_file_path, output_lang)

    if not Path(output_file_path).exists():
        raise FileNotFoundError(
            "File {0} does not exist".format(output_file_path), output_file_path
        )

    # Parse the output file into a dictionary
    output_data = parse_i18n_file(output_file_path)

    # Open the input file in read mode to read its contents
    with open(input_file_path, "r", encoding="utf-8") as f:
        input_file_contents = f.readlines()

    new_file_lines = []
    missing_message_keys = []
    for line in input_file_contents:
        # Skip comments and empty lines
        if line.startswith("#") or line.strip() == "":
            new_file_lines.append(line)
            continue

        # Extract the key and value on this line
        parts = line.strip().split("=", 1)
        if len(parts) == 1:
            # Skip this line if it is part of a multiline value
            continue

        key = parts[0]
        if key in output_data:
            translated_text = output_data[key]
            new_file_lines.append(f"{key}={translated_text}\n")
        else:
            missing_message_keys.append(key)

    # Open the output file in write mode to write the updated contents
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.writelines(new_file_lines)
    print(
        "i18n translation file sorted successfully:",
        output_file_path,
    )
    message_count = len(missing_message_keys)
    if message_count > 0:
        print(
            f"Note that {message_count} messages are missing in the "
            "sorted translation file:"
        )
        for key in missing_message_keys:
            print(key)


def main():
    """Build a CLI for calling sort_i18n_file"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input_file",
        required=True,
        type=str,
        help=(
            "filename of input Java properties file. "
            "Can be specified as a relative or absolute file path."
        ),
    )
    parser.add_argument(
        "-t",
        "--to",
        required=True,
        type=str,
        help=(
            "Language of the output file to be sorted. "
            "For example, use de to if it contains German translations."
        ),
    )
    parser.add_argument(
        "-o",
        "--output_file",
        required=False,
        type=str,
        help=(
            "filename of the output properties file to be sorted. "
            "Can be specified as a relative or absolute file path. "
            "Defaults to the input_file with the output language appended to it. "
            "For example, messages.properties would become messages_de.properties . "
            "If the file does not exist, the program will exit with an error."
        ),
    )
    args = parser.parse_args()
    sort_i18n_file(
        args.input_file,
        args.to,
        args.output_file,
    )


if __name__ == "__main__":
    main()
