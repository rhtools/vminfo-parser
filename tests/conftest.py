import typing as t
import pytest

from pathlib import Path


@pytest.fixture
def csv_file(tmp_path: Path) -> t.Generator[str, None, None]:
    csv_file = tmp_path / "test.csv"
    with open("tests/files/Test_Inventory_VMs.csv", "r") as src:
        with open(csv_file, "w") as dst:
            dst.writelines(src.readlines())
    yield str(csv_file)


@pytest.fixture
def xlsx_file(tmp_path: Path) -> t.Generator[str, None, None]:
    xlsx_file = tmp_path / "test.xlsx"
    with open("tests/files/Test_Inventory_VMs.xlsx", "rb") as src:
        with open(xlsx_file, "wb") as dst:
            dst.writelines(src.readlines())
    yield str(xlsx_file)
