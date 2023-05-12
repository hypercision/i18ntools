#!/usr/bin/env python
"""This script translates an i18n Java properties file into a new
i18n Java properties file of a different language
by making Rest API calls to Microsoft Azure Cognitive Services Translator.

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


def get_default_filepath(input_file_path, output_lang):
    """Returns the filepath for a new i18n Java properties file
    based on the filepath of the input file and the output language.

    The filepath returned with be in the same directory as the input file.
    The filename will be the same as the input file but with the
    output_lang appended to it. For example, "/dir/messages.properties"
    would become "/dir/messages_de.properties"
    and "/dir/messages_zh.properties" would become "/dir/messages_de.properties".

    Keyword arguments:
    input_file_path -- filepath of the file to translate
    output_lang -- language of the output file i.e. de for German
    """
    parts = os.path.splitext(input_file_path)
    file_path_without_extension = parts[0]
    # Use regex string replace to remove the language code
    # from the filename, if there is one.
    file_path_without_extension = re.sub("_.*$", "", file_path_without_extension)
    return f"{file_path_without_extension}_{output_lang}{parts[1]}"


def translate_file(
    input_file_path,
    output_lang,
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
        output_file_path = get_default_filepath(input_file_path, output_lang)

    # Set up the Translator API endpoint and subscription key
    translator_endpoint = (
        "https://api.cognitive.microsofttranslator.com"
        "/translate?api-version=3.0&from={0}&to={1}"
    ).format(input_lang, output_lang)
    # Read the API key from an environment variable
    subscription_key = os.environ["TRANSLATOR_API_SUBSCRIPTION_KEY"]

    # Parse the input file into a dictionary
    input_data = parse_i18n_file(input_file_path)

    # Open the input file in read mode to read its contents
    with open(input_file_path, "r", encoding="utf-8") as f:
        file_contents = f.readlines()

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

    response_object = response.json()

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

    # The commented out code below make an API call for each translation.
    # We can use this if we are getting errors due to the request being too big.

    # new_file_lines = []
    # for line in file_contents:
    #     # Skip comments and empty lines
    #     if line.startswith('#') or line.strip() == '':
    #         new_file_lines.append(line)
    #         continue

    #     # Extract the key and value on this line
    #     parts = line.strip().split('=', 1)
    #     if len(parts) == 1:
    #         # Skip this line if it is part of a multiline value
    #         continue

    #     key = parts[0]
    #     value = input_data[key]

    #     # Prepare the REST API request payload
    #     request_payload = [{
    #         'text': value
    #     }]

    #     # Make REST API call to Translator API to translate the value
    #     response = requests.post(
    #         translator_endpoint, headers=headers, json=request_payload, timeout=30
    #     )
    #     # Check if the REST API call was successful
    #     if response.status_code == 200:
    #         # Extract the translated text from the response
    #         translated_text = response.json()[0]['translations'][0]['text']
    #         new_file_lines.append(f'{key}={translated_text}\n')
    #     else:
    #         status_code_message = (
    #             f"Translation failed with status code: {response.status_code}"
    #         )
    #         print(status_code_message)
    #         print("Response:", response.text)
    #         print("translator_region:", translator_region)
    #         raise requests.HTTPError(status_code_message, response)

    # # Create a new i18n Java properties file in the specified output language
    # with open(output_file_path, 'w', encoding='utf-8') as f:
    #     f.writelines(new_file_lines)
    # print(
    #     "Translation completed successfully. Translated file saved to:",
    #     output_file_path,
    # )


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
    args = parser.parse_args()
    translate_file(
        args.input_file, args.to, args.output_file, args.from_lang, args.region
    )


if __name__ == "__main__":
    main()
