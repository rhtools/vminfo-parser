import re
import typing as t
from pathlib import Path

import pytest

from vminfo_parser import const as vm_const
from vminfo_parser.vminfo_parser import VMData


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
def extra_columns_non_windows_regex() -> t.Generator[re.Pattern, None, None]:
    pattern = re.compile(vm_const.EXTRA_COLUMNS_NON_WINDOWS_REGEX)
    yield pattern


@pytest.fixture(scope="session")
def extra_columns_windows_server_regex() -> t.Generator[re.Pattern, None, None]:
    pattern = re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX)
    yield pattern


@pytest.fixture(scope="session")
def extra_columns_windows_desktop_regex() -> t.Generator[re.Pattern, None, None]:
    pattern = re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX)
    yield pattern
