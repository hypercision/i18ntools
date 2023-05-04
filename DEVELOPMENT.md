# Testing

To run the tests, install the project dependencies in a [virtual environment](https://docs.python.org/3/library/venv.html#module-venv)
and then run tox:
```bash
python -m venv i18n_env
source i18n_env/bin/activate
pip install -r requirements.txt
tox
```

Alternatively, you can perform an editable installation inside of a virtual environment:
```bash
python -m venv i18n_env
source i18n_env/bin/activate
pip install -r requirements.txt
pip install --editable .
pytest
```

Anytime we need to add more packages, we install them like so and then update our requirements file:
```shell
pip install "<package_name>"
pip freeze > requirements.txt
```
