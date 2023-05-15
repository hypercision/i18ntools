# Contributing

Instructions:

- Fork the repository and clone it on your computer
- Install dependencies
- Update source code and add [tests](https://docs.pytest.org/) for any code you create
- Run the tests to verify your updates didn't break anything
- Once your code is ready, documented and tested, please make a [pull request](https://github.com/hypercision/i18ntools/pulls)

## Testing

### vcrpy

In addition to [`pytest`](https://docs.pytest.org/), we also use the [`vcrpy`](https://vcrpy.readthedocs.io/) library when writing our tests.

### tox

To run the tests, install the project dependencies in a [virtual environment](https://docs.python.org/3/library/venv.html#module-venv)
and then run [tox](https://tox.wiki/):
```bash
python -m venv i18n_env
source i18n_env/bin/activate
pip install -r requirements.txt
tox
```

The command to activate the virtual environment on Windows is:
```cmd
i18n_env\Scripts\activate.bat
```

Python “Virtual Environments” allow Python packages to be installed in an isolated location
for a particular application, rather than being installed globally.
You should run all your Python commands with your virtual environment activated.
Once you are done using Python, you can exit the virtual environment by entering `deactivate` in your terminal.

Anytime we need to add more packages, we install them like so and then update our requirements file:
```shell
pip install "<package_name>"
pip freeze > requirements.txt
```

### Editable installation

Alternatively, you can perform an [editable installation](https://setuptools.pypa.io/en/latest/userguide/development_mode.html)
of this package inside of a virtual environment:
```bash
python -m venv i18n_env
source i18n_env/bin/activate
pip install -r requirements.txt
pip install --editable .
pytest
```

Performing an editable installation of this package inside of a virtual environment allows you to call the CLI scripts
and test out actually calling the Azure API and translating files:
```bash
export TRANSLATOR_API_SUBSCRIPTION_KEY=<your_key>
translate -i=messages.properties -t=es
translate-missing -i=messages.properties -t=no
```

It also allows you to test out your changes by calling the updated methods in a Python file.
For example, you could make a file `changes.py`:
```python
import i18ntools.translate_missing


input_file = "i18n/messageBundle.properties"
output_lang = "es"
sort_file = True
i18ntools.translate_missing.translate_missing_messages(input_file, output_lang, sort_file)
```

And then execute it to confirm `translate_missing_messages` runs as expected:
```bash
export TRANSLATOR_API_SUBSCRIPTION_KEY=<your_key>
python changes.py
```
