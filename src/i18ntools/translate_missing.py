#!/usr/bin/env python
"""This script translates the messages in an i18n Java properties file that are
missing from an i18n Java properties file of a different language
by making Rest API calls to Microsoft Azure Cognitive Services Translator.

Requires the API secret key to be set in an environment variable
named TRANSLATOR_API_SUBSCRIPTION_KEY .

Note that this does not work properly for multiline translations
with an "=" character in them.
"""

import argparse
from pathlib import Path

import i18ntools.translate
from i18ntools.parse_i18n_file import parse_i18n_file
from i18ntools.sort_i18n_file import sort_i18n_file

# Default region for the Azure translator resource.
default_region = "eastus2"
# Default language to translate from.
default_lang = "en"


def translate_missing_messages(
    input_file_path,
    output_lang,
    sort_file=False,
    output_file_path=None,
    input_lang=default_lang,
    translator_region=default_region,
):
    if not Path(input_file_path).exists():
        raise FileNotFoundError(
            "File {0} does not exist".format(input_file_path), input_file_path
        )

    if output_file_path is None:
        # Make output_file_path be the input_file_path with the
        # output_lang appended to it. For example, "/dir/messages.properties"
        # would become "/dir/messages_de.properties".
        output_file_path = i18ntools.translate.get_default_filepath(
            input_file_path, output_lang
        )

    if not Path(output_file_path).exists():
        raise FileNotFoundError(
            "File {0} does not exist".format(output_file_path), output_file_path
        )

    # Parse the input file and output file into a dictionary
    input_data = parse_i18n_file(input_file_path)
    output_data = parse_i18n_file(output_file_path)

    # Find any i18n messages missing from the output file
    # and put those keys and values in the payload_data dictionary
    missing_message_keys = []
    payload_data = {}
    for key in input_data:
        if key not in output_data:
            missing_message_keys.append(key)
            payload_data[key] = input_data[key]

    message_count = len(missing_message_keys)
    if message_count == 0:
        print(
            f"No messages to translate. \n{output_file_path} already has all the "
            f"same messages as {input_file_path}"
        )
        return

    print(f"About to translate {message_count} missing messages")

    response_object = i18ntools.translate.make_api_call(
        payload_data, output_lang, input_lang, translator_region
    )

    # Open the output file in read mode to read its contents
    with open(output_file_path, "r", encoding="utf-8") as f:
        output_file_contents = f.readlines()

    for index, key in enumerate(missing_message_keys):
        # Extract the translated text from the response
        translated_text = response_object[index]["translations"][0]["text"]
        output_file_contents.append(f"{key}={translated_text}\n")

    # Open the output file in write mode to write the updated contents
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.writelines(output_file_contents)
    print(
        "Translation completed successfully. Translated messages added to file:",
        output_file_path,
    )
    if sort_file:
        sort_i18n_file(input_file_path, output_lang, output_file_path)


def main():
    """Build a CLI for calling translate_missing_messages"""
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
        "-f",
        "--from_lang",
        required=False,
        type=str,
        nargs="?",
        const=default_lang,
        default=default_lang,
        help="Language of the input file. Defaults to en",
    )
    parser.add_argument(
        "-t",
        "--to",
        required=True,
        type=str,
        help=(
            "Language of the output file. "
            "For example, use de to translate to German."
        ),
    )
    parser.add_argument(
        "-o",
        "--output_file",
        required=False,
        type=str,
        help=(
            "filename of the output properties file with the missing messages. "
            "Can be specified as a relative or absolute file path. "
            "Defaults to the input_file with the output_lang appended to it. "
            "For example, messages.properties would become messages_de.properties . "
            "If the file does not exist, the program will exit with an error."
        ),
    )
    parser.add_argument(
        "-r",
        "--region",
        required=False,
        type=str,
        nargs="?",
        const=default_region,
        default=default_region,
        help="region of the Azure translator resource. Defaults to eastus2",
    )
    parser.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help=(
            "sort the messages in the output file in the same order as the "
            "input file. If this is not specified, then the missing messages "
            "will be appended at the end of the output file."
        ),
    )
    args = parser.parse_args()
    translate_missing_messages(
        args.input_file,
        args.to,
        args.sort,
        args.output_file,
        args.from_lang,
        args.region,
    )


if __name__ == "__main__":
    main()
