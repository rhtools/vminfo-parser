import logging
import re
import typing as t
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import vminfo_parser.const as vm_const
from vminfo_parser.vmdata import VMData

from .. import const as test_const


def test_get_file_type(datafile: tuple[bool, Path]) -> None:
    empty, filepath = datafile
    mime = vm_const.MIME.get(filepath.suffix.removeprefix("."))
    result = VMData.get_file_type(filepath)

    if empty:
        assert result != mime
    else:
        assert result == mime


def test_from_file(datafile: tuple[bool, Path], caplog: pytest.LogCaptureFixture) -> None:
    empty, filepath = datafile

    if empty:
        with pytest.raises(SystemExit):
            result = VMData.from_file(filepath)
            assert result is None
        assert caplog.record_tuples == [
            ("vminfo_parser.vmdata", logging.CRITICAL, "File passed in was neither a CSV nor an Excel file")
        ]
    else:
        result = VMData.from_file(filepath)
        assert isinstance(result, VMData)
        assert isinstance(result.df, pd.DataFrame)
        assert result.df.shape == test_const.TESTFILE_SHAPE


@pytest.mark.parametrize(
    test_const.TEST_DATAFRAMES[0].keys(),
    [(pd.DataFrame(item["df"]), item["unit"], item["version"]) for item in test_const.TEST_DATAFRAMES],
    ids=[f"Version {item['version']}" for item in test_const.TEST_DATAFRAMES],
)
def test_set_column_headings(df: pd.DataFrame, unit: str, version: int) -> None:
    expected_headers = deepcopy(vm_const.COLUMN_HEADERS.get(f"VERSION_{version}").copy())
    expected_headers["unitType"] = unit

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


@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_add_extra_columns_from_datafile(vmdata_with_headers: VMData) -> None:
    original_df = vmdata_with_headers.df.copy()
    unmodified_columns = list(set(original_df.columns).difference(set(vm_const.EXTRA_COLUMNS_DEST)))

    vmdata_with_headers.add_extra_columns()

    # Validate that temporary columns are dropped
    assert (
        len(
            set(vm_const.EXTRA_WINDOWS_SERVER_COLUMNS + vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS).intersection(
                set(vmdata_with_headers.column_headers)
            )
        )
        == 0
    )

    # Validate that added columns exist
    assert all(col in vmdata_with_headers.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    # Validate that no other columns were changed
    assert original_df[unmodified_columns].equals(vmdata_with_headers.df[unmodified_columns])


@pytest.mark.parametrize(
    "vmdata",
    [VMData(df=pd.DataFrame(item["df"])) for item in test_const.TEST_DATAFRAMES],
    ids=[f"Version {item['version']}" for item in test_const.TEST_DATAFRAMES],
)
def test_add_extra_columns_from_df(vmdata: VMData) -> None:
    vmdata.set_column_headings()
    vmdata.add_extra_columns()

    assert all(vmdata.df[vm_const.EXTRA_COLUMNS_DEST[0]].notnull())


@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_add_extra_columns_bypass(vmdata_with_headers: VMData, caplog: pytest.LogCaptureFixture) -> None:
    vmdata_with_headers.add_extra_columns()

    original_df = vmdata_with_headers.df.copy()
    vmdata_with_headers.add_extra_columns()

    # Validate that temporary columns do not exist
    assert (
        len(
            set(vm_const.EXTRA_WINDOWS_SERVER_COLUMNS + vm_const.EXTRA_WINDOWS_DESKTOP_COLUMNS).intersection(
                set(vmdata_with_headers.column_headers)
            )
        )
        == 0
    )

    # Validate that added columns exist
    assert all(col in vmdata_with_headers.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    # Validate that no columns were changed
    assert original_df.equals(vmdata_with_headers.df)

    # Validate that log stmt from else block was executed
    assert caplog.record_tuples == [("vminfo_parser.vmdata", logging.INFO, "All columns already exist")]


@pytest.mark.parametrize(
    "osname,expected",
    [(name, expected) for name, expected in test_const.SERVER_NAME_MATCHES.items()],
    ids=[name if len(name) < 36 else name[0:32] + "..." for name in test_const.SERVER_NAME_MATCHES.keys()],
)
def test_extra_column_regex(
    extra_columns_regexs: dict[str, re.Pattern], osname: str, expected: dict[str, str] | None
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


@pytest.mark.parametrize("datafile", ["Site_example.xlsx"], indirect=["datafile"])
def test_create_site_specific_dataframe(vmdata_with_headers: VMData) -> None:
    result = vmdata_with_headers.create_site_specific_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert not result.empty

    expected_columns = ["Site Name", "Site_RAM_Usage", "Site_Disk_Usage", "Site_CPU_Usage", "Site_VM_Count"]
    assert all(col in result.columns for col in expected_columns)

    # Check that the sum of Site_RAM_Usage matches the total RAM in the original DataFrame
    total_ram_original = vmdata_with_headers.df["VM MEM (GB)"].sum()
    total_ram_result = result["Site_RAM_Usage"].sum()

    assert pytest.approx(total_ram_original) == total_ram_result

    # Check that the sum of Site_Disk_Usage matches the total Disk in the original DataFrame
    total_disk_original = np.ceil(vmdata_with_headers.df["VM Provisioned (GB)"] / 1024).astype(int).sum()

    total_disk_result = result["Site_Disk_Usage"].sum()

    assert pytest.approx(total_disk_original) == total_disk_result

    # Check that the sum of Site_CPU_Usage matches the total CPU in the original DataFrame
    total_cpu_original = vmdata_with_headers.df["VM CPU"].sum()
    total_cpu_result = result["Site_CPU_Usage"].sum()

    assert pytest.approx(total_cpu_original) == total_cpu_result

    # Check that the sum of Site_VM_Count matches the number of rows in the original DataFrame
    total_vms_original = len(vmdata_with_headers.df)
    total_vms_result = result["Site_VM_Count"].sum()

    assert total_vms_original == total_vms_result


@pytest.mark.parametrize(
    "vmdata",
    [
        VMData(
            df=pd.DataFrame(
                columns=["VM OS", "VM MEM (GB)", "VM CPU", "VM Provisioned (GB)", "Environment", "Site Name"]
            )
        )
    ],
    ids=["empty"],
)
def test_create_site_specific_dataframe_empty(vmdata_with_headers: VMData) -> None:
    result = vmdata_with_headers.create_site_specific_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert result.empty
