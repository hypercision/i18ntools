#!/usr/bin/env python
"""This script translates an i18n Java properties file into a new
i18n Java properties file of a different language
by making REST API calls to Microsoft Azure Cognitive Services Translator.

Requires the API secret key to be set in an environment variable
named TRANSLATOR_API_SUBSCRIPTION_KEY .
If --output_file already exists, then the file will be overwritten.

Note that this does not work properly for multiline translations
with an "=" character in them.
"""

import argparse
import os
import re
from pathlib import Path

import requests
from i18ntools.parse_i18n_file import parse_i18n_file

# Default region for the Azure translator resource.
default_region = "eastus2"
# Default language to translate from.
default_lang = "en"

# Matches a Java locale suffix at the end of a filename stem, e.g.
# "_en", "_en_GB", "_es_419", "_zh_Hant", "_zh_Hant_TW".
# Format: _language[_Script][_REGION]
_LOCALE_SUFFIX_PATTERN = re.compile(
    r"_[a-z]{2,3}"  # language: ISO 639 code, e.g. en, de, fil
    r"(?:_[A-Z][a-z]{3})?"  # optional script: ISO 15924 code, e.g. Hant
    r"(?:_(?:[A-Z]{2}|\d{3}))?"  # optional region: ISO 3166 or UN M.49, e.g. GB, 419
    r"$"
)


def get_default_filepath(input_file_path, output_lang):
    """Returns the filepath for a new i18n Java properties file
    based on the filepath of the input file and the output language.

    The filepath returned will be in the same directory as the input file.
    The filename will be the same as the input file but with the
    output_lang appended to it. For example, "/dir/messages.properties"
    would become "/dir/messages_de.properties"
    and "/dir/messages_zh.properties" would become "/dir/messages_de.properties".

    Only a trailing locale suffix in the filename (e.g. "_en", "_en_GB",
    "_zh_Hant_TW") is replaced. Underscores elsewhere in the filename or
    anywhere in the directory path are preserved.

    Keyword arguments:
    input_file_path -- filepath of the file to translate
    output_lang -- language of the output file i.e. de for German
    """
    input_file_path = str(input_file_path)
    # Only operate on the filename, so the directory path is never modified.
    filename = os.path.basename(input_file_path)
    directory_prefix = input_file_path[: len(input_file_path) - len(filename)]

    stem, extension = os.path.splitext(filename)
    # Remove the existing locale suffix from the filename, if there is one.
    stem = _LOCALE_SUFFIX_PATTERN.sub("", stem, count=1)
    return f"{directory_prefix}{stem}_{output_lang}{extension}"


def make_api_call(
    input_data,
    output_lang,
    input_lang=default_lang,
    translator_region=default_region,
):
    """Returns the JSON response of the API call as a dictionary.

    Keyword arguments:
    input_data -- a dictionary of the keys and values of the i18n translations
    output_lang -- the language of the output file i.e. de for German.
    input_lang -- the language of the input file i.e. de for German. (default en)
    translator_region -- the region of the Azure translator resource. (default eastus2)
    """
    # Set up the Translator API endpoint and subscription key
    translator_endpoint = (
        "https://api.cognitive.microsofttranslator.com"
        "/translate?api-version=3.0&from={0}&to={1}"
    ).format(input_lang, output_lang)
    # Read the API key from an environment variable
    subscription_key = os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"]

    # Set up the REST API request headers
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Ocp-Apim-Subscription-Region": translator_region,
    }

    message_count = len(input_data.keys())
    print(f"About to translate {message_count} messages")

    # Set up the REST API request payload
    request_payload = []
    for key, value in input_data.items():
        # Add text to translate to the REST API request payload
        request_payload.append({"text": value})

    # Make the REST API call to Translator API to translate the values
    # https://learn.microsoft.com/en-us/azure/cognitive-services/translator/reference/v3-0-translate
    response = requests.post(
        translator_endpoint, headers=headers, json=request_payload, timeout=30
    )
    # Exit with an error if the REST API call was not successful
    if response.status_code != 200:
        status_code_message = (
            f"Translation failed with status code: {response.status_code}"
        )
        print(status_code_message)
        print("Response:", response.text)
        print("translator_region:", translator_region)
        raise requests.HTTPError(status_code_message, response)

    return response.json()


def translate_file(
    input_file_path,
    output_lang,
    output_file_path=None,
    input_lang=default_lang,
    translator_region=default_region,
    remove_backslashes=False,
):
    if not Path(input_file_path).exists():
        raise FileNotFoundError(f"File {input_file_path} does not exist")

    if output_file_path is None:
        # Make output_file_path be the input_file_path with the
        # output_lang appended to it. For example, "/dir/messages.properties"
        # would become "/dir/messages_de.properties".
        output_file_path = get_default_filepath(input_file_path, output_lang)

    # Parse the input file into a dictionary
    input_data = parse_i18n_file(input_file_path, remove_backslashes)

    # Open the input file in read mode to read its contents
    with open(input_file_path, "r", encoding="utf-8") as f:
        file_contents = f.readlines()

    response_object = make_api_call(
        input_data, output_lang, input_lang, translator_region
    )

    index = 0
    new_file_lines = []
    for line in file_contents:
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
        # Extract the translated text from the response
        translated_text = response_object[index]["translations"][0]["text"]
        new_file_lines.append(f"{key}={translated_text}\n")
        index += 1

    # Create a new i18n Java properties file in the specified output language
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.writelines(new_file_lines)
    print(
        "Translation completed successfully. Translated file saved to:",
        output_file_path,
    )


def main():
    """Build a CLI for calling translate_file"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input_file",
        required=True,
        type=str,
        help=(
            "filename of input Java properties file to translate. "
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
            "filename of the output properties file. Can be specified as a "
            "relative or absolute file path. Defaults to the input_file with "
            "the output language appended to it. For example, messages.properties "
            "would become messages_de.properties"
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
        "-rbs",
        "--remove_backslashes",
        action="store_true",
        help=(
            "any backslashes from multiline values in the input file "
            "will not be included in the text that gets translated."
        ),
    )
    args = parser.parse_args()
    translate_file(
        args.input_file,
        args.to,
        args.output_file,
        args.from_lang,
        args.region,
        args.remove_backslashes,
    )


if __name__ == "__main__":
    main()
