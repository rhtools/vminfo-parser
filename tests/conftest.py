import typing as t
from pathlib import Path

import pytest


@pytest.fixture(params=["csv", "xlsx", "emptycsv", "emptyxlsx"])
def datafile(
    tmp_path: Path, request: pytest.FixtureRequest
) -> t.Generator[tuple[str, bool, str], None, None]:
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
