# Contributing

## Conventional Commits

All commits on `dev` and `main` must follow the [Conventional Commit Standard](https://www.conventionalcommits.org/en/v1.0.0/).
The following types are supported:

* chore - Dependancy Security Updates, Merges, Cleanup.
* ci - Changes to CI/CD workflows
* docs - Changes to Documentations
* feat - New Features or Feature Enhancements
* fix - Bugfixes (should linked to an issue)
* perf - Perfomance Enhancements
* style - Code Style Changes
* refactor - Refactor of code for maintenance reasons (should use feat or perf if appopriate)
* test - Changes to Tests.  

While not explicityly required for individual commits that will be squash merged into dev,  it is advantagous to follow the standard for consistentency.

## PRs

All Pull requests should be opened against the `dev` branch.
All PRs titles must conform to the conventional commit standards.
All Merges into `dev` should be accomplished with squash merges,  with the PR title as the commit message.
Because of this, All PRs should cover a single change.
Shoehorning other changes into a PR will make this disappear from the release notes and make them difficult to revert.  

When PRs are merged into `dev` a prerelease will be built with with the appropriate semantic version based on the commit message along with a `-dev` tag.

## Releases

Releases will be accomplished by PR from `dev` to `main`.
The PRs will be Merged to `main` retaining all the presumably Conventional Commit compliant commits, for use with generating semanatic version.
Merges into `main` will automatically trigger a release with a semantic version based on the commits pushed.  

## Testing

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

### Image Comparison

Plots are tested using `pytest-mpl` using hash and image comparison.  

When changes are made, or new tests are added, baseline images and hashes must be generated/updated before the tests will pass.

Baseline images as well as hashes are stored in [tests/images/](images)

The following command can be run prior to commit in order to generate these.

```sh
pytest --mpl-generate-path=tests/images --mpl-generate-hash-library=tests/images/hashes.json tests/test_visualizer.py
```