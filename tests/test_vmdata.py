import re
import typing as t
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


def test_set_column_headings_invalid() -> None:
    vmdata = VMData(
        df=pd.DataFrame(
            {
                "VM OS Name": ["Windows 10", "Ubuntu 20.04", "CentOS 7"],
                "Environments": ["Prod", "Dev", "Prod"],
                "VM MEM": [8, 16, 32],
                "VM Provisioned Disk": [100, 200, 300],
            }
        )
    )

    with pytest.raises(ValueError):
        vmdata.set_column_headings()

    assert vmdata.column_headers == {}


@pytest.mark.usefixtures("datafile")
@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_add_extra_columns(vmdata: VMData) -> None:
    vmdata.set_column_headings()
    original_df = vmdata.df.copy()
    unmodified_columns = list(set(original_df.columns).difference(set(vm_const.EXTRA_COLUMNS_DEST)))

    vmdata.add_extra_columns()

    assert (
        len(
            set(vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS + vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS).intersection(
                set(vmdata.column_headers)
            )
        )
        == 0
    )

    assert all(col in vmdata.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    assert original_df[unmodified_columns].equals(vmdata.df[unmodified_columns])


@pytest.mark.parametrize(
    "osname,expected",
    [(name, expected) for name, expected in test_const.SERVER_NAME_MATCHES.items() if "Microsoft" not in name],
    ids=[name for name in test_const.SERVER_NAME_MATCHES.keys() if "Microsoft" not in name],
)
def test_extra_column_non_windows_regex(
    extra_columns_non_windows_regex: re.Pattern, osname: str, expected: t.Optional[dict[str, str]]
) -> None:
    re_match = extra_columns_non_windows_regex.match(osname)

    if expected is None:
        assert re_match is None
    else:
        assert re_match.groupdict() == expected


@pytest.mark.parametrize(
    "osname,expected",
    [
        (name, expected)
        for name, expected in test_const.SERVER_NAME_MATCHES.items()
        if "Microsoft" in name and "Server" in name
    ],
    ids=[name for name in test_const.SERVER_NAME_MATCHES.keys() if "Microsoft" in name and "Server" in name],
)
def test_extra_column_windows_server_regex(
    extra_columns_windows_server_regex: re.Pattern, osname: str, expected: t.Optional[dict[str, str]]
) -> None:
    re_match = extra_columns_windows_server_regex.match(osname)

    if expected is None:
        assert re_match is None
    else:
        assert re_match.groupdict() == expected


@pytest.mark.parametrize(
    "osname,expected",
    [
        (name, expected)
        for name, expected in test_const.SERVER_NAME_MATCHES.items()
        if "Microsoft" in name and "Server" not in name
    ],
    ids=[name for name in test_const.SERVER_NAME_MATCHES.keys() if "Microsoft" in name and "Server" not in name],
)
def test_extra_column_windows_desktop_regex(
    extra_columns_windows_desktop_regex: re.Pattern, osname: str, expected: t.Optional[dict[str, str]]
) -> None:
    re_match = extra_columns_windows_desktop_regex.match(osname)

    if expected is None:
        assert re_match is None
    else:
        assert re_match.groupdict() == expected
