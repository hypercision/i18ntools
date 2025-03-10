
<h1 align="center">
  i18ntools
</h1>

<h4 align="center">Translate i18n Java properties files to desired language(s).</h4>

<p align="center">
  <a href="#description">Description</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/i18ntools" alt="Supported Versions">
    <img src="https://img.shields.io/pypi/pyversions/i18ntools.svg" />
  </a>
  <a href="https://github.com/hypercision/i18ntools/actions/workflows/python.yml" alt="Unit tests">
    <img src="https://github.com/hypercision/i18ntools/actions/workflows/python.yml/badge.svg" />
  </a>
  <a href="LICENSE" alt="License">
    <img src="https://img.shields.io/github/license/hypercision/i18ntools" />
  </a>
</p>

## Description

i18ntools is a collection of Python scripts to help translate your Java properties internationalization files
using [Azure Cognitive Services Translator](https://azure.microsoft.com/en-us/services/cognitive-services/translator/).

### What does each script do?

- [translate.py](https://github.com/hypercision/i18ntools/blob/main/src/i18ntools/translate.py) translates an entire i18n Java properties file into a new i18n Java properties file of a different language.
- [translate_missing.py](https://github.com/hypercision/i18ntools/blob/main/src/i18ntools/translate_missing.py) translates the messages in an i18n Java properties file that are missing
from an i18n Java properties file of a different language.
The missing messages will be appended at the end of the output file unless the `--sort` option is used.
Note: using the `--sort` option will delete comments in the output file that are not present in the input file.
- [parse_i18n_file.py](https://github.com/hypercision/i18ntools/blob/main/src/i18ntools/parse_i18n_file.py) reads an i18n Java properties file and returns the data as a dictionary.
- [sort_i18n_file.py](https://github.com/hypercision/i18ntools/blob/main/src/i18ntools/sort_i18n_file.py) sorts the messages in a given i18n Java properties file so that they are
in the same order as the messages in a different i18n Java properties file.
Using this script will delete comments in the sorted output file that are not present in the input file.

## Installation

You can install the i18ntools package using pip:

```shell
python -m pip install i18ntools
```

i18ntools officially supports Python 3.8+.

It is recommended to install i18ntools in a [virtual environment](https://docs.python.org/3/library/venv.html#module-venv)
rather than being installed globally:
```shell
python -m venv i18n_env
source i18n_env/bin/activate
python -m pip install i18ntools
```

When this package is installed, CLI executables of the scripts will be installed on the path of your virtual environment.
```shell
translate --help
translate-missing --help
parse-i18n-file --help
sort-i18n-file --help
```

## Usage

Before using `translate.py` or `translate_missing.py`, your Azure API secret key must be set in
an environment variable named `TRANSLATOR_API_SUBSCRIPTION_KEY`.
```shell
export TRANSLATOR_API_SUBSCRIPTION_KEY=<your_key>
```
You can accomplish this on Windows with the following command:
```cmd
C:\>set TRANSLATOR_API_SUBSCRIPTION_KEY=<your_key>
```
Suppose you have the following in a file named `/home/docs/example.properties`:
```properties
default.invalid.min.message=Property [{0}] of class [{1}] with value [{2}] is less than minimum value [{3}]

# Track 4 on Expert In A Dying Field
TheBeths.YourSide.lyrics=I want to see you knocking at the door. \
    I wanna leave you out there waiting in the downpour. \
    Singing that you’re sorry, dripping on the hall floor.
instructor.submitWithCustomTime.customSubmitTS.missing.error=The customSubmitTS parameter is missing. \
    It must be present and of type Date.

# SessionItem.itemID is the first parameter
instructorService.removeSession.success={0} session removed.

handshake.register.suspended.error=The trial period has ended for your account \
    and you can no longer use the application.
handshake.register.disabledException.error=Instructor is disabled
```

When you run:
```shell
translate -i=/home/docs/example.properties -t=es
```
Then a new file named `/home/docs/example_es.properties` will be saved and contain Spanish translations
of the input file, with the comments preserved:
```properties
default.invalid.min.message=La propiedad [{0}] de la clase [{1}] con valor [{2}] es menor que el valor mínimo [{3}]

# Track 4 on Expert In A Dying Field
TheBeths.YourSide.lyrics=Quiero verte llamando a la puerta. \
    Quiero dejarte ahí afuera esperando bajo el aguacero. \
    Cantando que lo sientes, goteando en el piso del pasillo.
instructor.submitWithCustomTime.customSubmitTS.missing.error=Falta el parámetro customSubmitTS. \
    Debe estar presente y ser de tipo Fecha.

# SessionItem.itemID is the first parameter
instructorService.removeSession.success={0} sesión eliminada.

handshake.register.suspended.error=El período de prueba ha finalizado para su cuenta \
    y ya no puede usar la aplicación.
handshake.register.disabledException.error=El instructor está deshabilitado
```

### Options

These are the options for `translate.py`.
Details about how to use each file can be found by running it with the `--help` flag.

<!-- markdownlint-disable -->
| Key | Alias | Description | Default |
| --------------------------- | ----- | ----------------------- | --------------- |
| --help | -h | All available options. | / |
| --region | -r | Region of the Azure translator resource. | eastus2 |
| --input_file [required] | -i | Path to a `.properties` file to translate. | / |
| --from_lang | -f | From which language you want to translate. | en |
| --to [required]   | -t | To which language you want to translate. For example, use de to translate to German. | / |
| --output_file | -o | Path where the translated `.properties` file will be saved. Overwrites any existing file. | input_file with the output language appended to the filename; i.e., `messages.properties` would become `messages_de.properties`. |
<!-- markdownlint-restore -->

### Translate multiple files

If you want to tranlsate multiple entire files, you can create a Python file that imports the `i18ntools.translate` module
and calls `translate_file`:
```python
from i18ntools.translate import translate_file


files = [
    "app/Admin/i18n/messageBundle.properties",
    "app/Device/crud/i18n/messageBundle.properties",
    "app/Login/i18n/messageBundle.properties",
]

output_lang = "es"

for input_file in files:
    translate_file(input_file, output_lang)
```

If you want to tranlsate missing messages from multiple files, you can create a Python file that imports the
`i18ntools.translate_missing` module and calls `translate_missing_messages`:
```python
from i18ntools.translate_missing import translate_missing_messages


files = [
    "app/Admin/i18n/messageBundle.properties",
    "app/Device/crud/i18n/messageBundle.properties",
    "app/Login/i18n/messageBundle.properties",
]

for input_file in files:
    # This assumes the following files exist:
    # app/Admin/i18n/messageBundle_es.properties
    # app/Device/crud/i18n/messageBundle_es.properties
    # app/Login/i18n/messageBundle_es.properties
    translate_missing_messages(input_file, output_lang="es", sort_file=True)
```

## Obtaining API keys

- Azure
  - Follow the instructions [here](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=nodejs#prerequisites).

## License

- [MIT](LICENSE)

## Contribute

Contributions are more than welcome. Please see the [contribution instructions](https://github.com/hypercision/i18ntools/blob/main/CONTRIBUTING.md).
