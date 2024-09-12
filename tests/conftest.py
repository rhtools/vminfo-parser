import re
import typing as t
from pathlib import Path

import pytest
import yaml

from vminfo_parser import const as vm_const
from vminfo_parser.vminfo_parser import VMData

from . import const as test_const


@pytest.fixture(params=["csv", "xlsx", "emptycsv", "emptyxlsx"])
def datafile(tmp_path: Path, request: pytest.FixtureRequest) -> t.Generator[tuple[str, bool, str], None, None]:
    datafile = tmp_path / "test"
    suffix = request.param.removeprefix("empty")
    datafile.with_suffix(f".{suffix}")
    empty = True if "empty" in request.param else False
    if empty:
        datafile.touch()
    else:
        with open(f"tests/files/Test_Inventory_VMs.{suffix}", "rb") as src:
            with open(datafile, "wb") as dst:
                dst.writelines(src.readlines())
    yield (suffix, empty, str(datafile))


@pytest.fixture
def vmdata(request: pytest.FixtureRequest) -> t.Generator[VMData, None, None]:
    _, _, filename = request.getfixturevalue("datafile")
    yield VMData.from_file(filename)


@pytest.fixture(scope="session")
def extra_columns_regexs() -> t.Generator[dict[str, re.Pattern], None, None]:
    yield {
        "non_windows": re.compile(vm_const.EXTRA_COLUMNS_NON_WINDOWS_REGEX),
        "windows_server": re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX),
        "windows_desktop": re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX),
    }


@pytest.fixture(
    params=test_const.CLI_OPTIONS.values(),
    ids=test_const.CLI_OPTIONS.keys(),
)
def config_dict(request: pytest.FixtureRequest) -> t.Generator[dict, None, None]:
    default_dict = {
        "breakdown-by-terabyte": False,
        "file": "tests/files/Test_Inventory_VMs.xlsx",
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
def yaml_config(tmp_path: Path, config_dict: dict) -> t.Generator[str, None, None]:
    yamlfile = tmp_path / "config.yaml"
    with open(yamlfile, "w") as file:
        yaml.dump(config_dict, file)
    yield str(yamlfile)


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
