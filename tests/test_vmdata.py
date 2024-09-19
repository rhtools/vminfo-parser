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
                    "VM CPU": [4, 8, 12],
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
                    "CPUs": [4, 8, 12],
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

    # Validate that temporary columns are dropped
    assert (
        len(
            set(vm_const.EXTRA_WINDOWS_SERVER_COLUMNS + vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS).intersection(
                set(vmdata.column_headers)
            )
        )
        == 0
    )

    # Validate that added columns exist
    assert all(col in vmdata.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    # Validate that no other columns were changed
    assert original_df[unmodified_columns].equals(vmdata.df[unmodified_columns])


@pytest.mark.usefixtures("datafile")
@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_add_extra_columns_bypass(vmdata: VMData, capsys: pytest.CaptureFixture) -> None:
    vmdata.set_column_headings()
    vmdata.add_extra_columns()

    original_df = vmdata.df.copy()
    vmdata.add_extra_columns()
    output = capsys.readouterr()

    # Validate that temporary columns do not exist
    assert (
        len(
            set(vm_const.EXTRA_WINDOWS_SERVER_COLUMNS + vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS).intersection(
                set(vmdata.column_headers)
            )
        )
        == 0
    )

    # Validate that added columns exist
    assert all(col in vmdata.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    # Validate that no columns were changed
    assert original_df.equals(vmdata.df)

    # Validate that print stmt from else block was executed
    assert output.out == "All columns already exist\n"


@pytest.mark.parametrize(
    "osname,expected",
    [(name, expected) for name, expected in test_const.SERVER_NAME_MATCHES.items()],
    ids=[name for name in test_const.SERVER_NAME_MATCHES.keys()],
)
def test_extra_column_regex(
    extra_columns_regexs: dict[str, re.Pattern], osname: str, expected: t.Optional[dict[str, str]]
) -> None:
    re_matches = {}
    for name, matcher in extra_columns_regexs.items():
        re_matches[name] = matcher.match(osname)

    match expected.get("OS_Name") if expected is not None else None:
        case None:
            # Validate that no regexs matched
            assert all(re_match is None for re_match in re_matches.values())
        case "Microsoft Windows Server":
            # Validate that only the windows server regex matched and has expected results
            assert all(
                re_match.groupdict() == expected if name == "windows_server" else re_match is None
                for name, re_match in re_matches.items()
            )
        case "Microsoft Windows":
            # Validate that only the windows desktop regex matched and has expected results
            assert all(
                re_match.groupdict() == expected if name == "windows_desktop" else re_match is None
                for name, re_match in re_matches.items()
            )
        case _:
            # Validate that only the non windows regex matched and has expected results
            assert all(
                re_match.groupdict() == expected if name == "non_windows" else re_match is None
                for name, re_match in re_matches.items()
            )
