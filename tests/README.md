# Testing

All tests are executed by `pytest`.  

Testing requirements are stored in [tests/requirements.txt](requirements.txt), and supplements the [development](../dev-requirements.txt) and [execution requirements](../requirements.txt).  Testing and Execution requirements must be installed for testing.

```sh
pip isntall -r requierments.txt
pip install -r tests/requirements.txt
```

alternatively,  if using editable installs

```sh
pip install -e ".[test,dev]"
```

Assuming dependancies are installed as above, tests can be executed with:

```sh
pytest
```

Individual test files can be run by adding the file path to the command.  For example, to only run the tests in test_config.py

```sh
pytest tests/test_config.py
```

## Image Comparison

Plots are tested using `pytest-mpl` using hash and image comparison.  

When changes are made, or new tests are added, baseline images and hashes must be generated/updated before the tests will pass.

Baseline images as well as hashes are stored in [tests/images/](images)

The following command can be run prior to commit in order to generate these.

```sh
pytest --mpl-generate-path=tests/images --mpl-generate-hash-library=tests/images/hashes.json tests/test_visualizer.py
```