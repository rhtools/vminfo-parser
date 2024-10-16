import typing as t
from pathlib import Path, PosixPath

import pytest
import yaml

import vminfo_parser.config as vm_config

from . import const as test_const


def pytest_configure(config: pytest.Config) -> None:
    vm_config._IS_TEST = True


def pytest_unconfigure(config: pytest.Config) -> None:
    vm_config._IS_TEST = False


def yaml_path_representer(dumper: yaml.Dumper, path: Path) -> yaml.ScalarNode:
    return dumper.represent_str(str(path))


yaml.add_representer(PosixPath, yaml_path_representer)


@pytest.fixture(
    params=test_const.CLI_OPTIONS.values(),
    ids=test_const.CLI_OPTIONS.keys(),
)
def config_dict(request: pytest.FixtureRequest) -> t.Generator[dict, None, None]:
    default_dict = {
        "breakdown-by-terabyte": False,
        "file": Path("tests/files/Test_Inventory_VMs.xlsx"),
        "generate-graphs": False,
        "get-disk-space-ranges": False,
        "get-os-counts": False,
        "get-supported-os": False,
        "get-unsupported-os": False,
        "minimum-count": 0,
        "os-name": None,
        "over-under-tb": False,
        "output-os-by-version": False,
        "prod-env-labels": None,
        "show-disk-space-by-os": False,
        "sort-by-env": None,
    }
    if isinstance(request.param, dict):
        default_dict.update(request.param)
    yield default_dict


@pytest.fixture
def cli_args(config_dict: dict) -> t.Generator[list[str], None, None]:
    args = []
    for key, value in config_dict.items():
        match value:
            case True:
                args.append(f"--{key}")
            case None:
                pass
            case False:
                pass
            case _:
                args.append(f"--{key}")
                args.append(str(value))
    yield args
