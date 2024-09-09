from copy import deepcopy

import pandas as pd
import pytest

import vminfo_parser.const as vm_const
from vminfo_parser.vminfo_parser import VMData

from . import const as test_const


def test_get_file_type(datafile: tuple[str, bool, str]) -> None:
    filename = datafile[2]
    empty = datafile[1]
    mime = vm_const.MIME.get(datafile[0])
    result = VMData.get_file_type(filename)

    if empty:
        assert result != mime
    else:
        assert result == mime


def test_from_file(datafile: tuple[str, bool, str], capsys: pytest.CaptureFixture) -> None:
    filename = datafile[2]
    empty = datafile[1]

    if empty:
        with pytest.raises(SystemExit):
            result = VMData.from_file(filename)
            assert result is None
        output = capsys.readouterr()
        assert output.out == "File passed in was neither a CSV nor an Excel file\nBailing...\n"
    else:
        result = VMData.from_file(filename)
        assert isinstance(result, VMData)
        assert isinstance(result.df, pd.DataFrame)
        assert result.df.shape == test_const.TESTFILE_SHAPE


@pytest.mark.parametrize(
    ["df", "units", "version"],
    [
        (
            pd.DataFrame(
                {
                    "VM OS": ["Windows 10", "Ubuntu 20.04", "CentOS 7"],
                    "Environment": ["Prod", "Dev", "Prod"],
                    "VM MEM (GB)": [8, 16, 32],
                    "VM Provisioned (GB)": [100, 200, 300],
                }
            ),
            "GB",
            1,
        ),
        (
            pd.DataFrame(
                {
                    "OS according to the configuration file": [
                        "Windows 10",
                        "Ubuntu 20.04",
                        "CentOS 7",
                    ],
                    "ent-env": ["Prod", "Dev", "Prod"],
                    "Memory": [8, 16, 32],
                    "Total disk capacity MiB": [100, 200, 300],
                }
            ),
            "MB",
            2,
        ),
    ],
    ids=["Version 1", "Version 2"],
)
def test_set_column_headings(df: pd.DataFrame, units: str, version: int) -> None:
    expected_headers = deepcopy(vm_const.COLUMN_HEADERS.get(f"VERSION_{version}").copy())
    expected_headers["unitType"] = units

    vmdata = VMData(df=df)
    vmdata.set_column_headings()

    assert vmdata.column_headers == expected_headers
    assert all([version is not vmdata.column_headers for version in vm_const.COLUMN_HEADERS.values()])
