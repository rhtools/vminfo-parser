import csv
import glob
import logging
import re
from copy import deepcopy
from pathlib import Path

import chardet
import numpy as np
import pandas as pd
import pytest

import vminfo_parser.const as vm_const
from vminfo_parser.vmdata import VMData, _categorize_environment


from .. import const as test_const


@pytest.mark.parametrize(
    "is_empty,file_extension,data",
    [
        (True, ".csv", ""),
        (
            False,
            ".csv",
            [["Name", "Age", "City"], ["Bob", 28, "Maine"], ["Frank", 24, "Florida"], ["Roxanne", 32, "Ontario"]],
        ),
        (True, ".xlsx", ""),
        (False, ".xlsx", {"A": [1, 2], "B": [3, 4]}),
    ],
)
def test_get_file_type(tmp_path, is_empty, file_extension, data):
    # Create a test file with the specified extension
    filepath = tmp_path / f"test{file_extension}"
    if is_empty:
        filepath.touch()
    elif file_extension == ".csv":
        with open(filepath, mode="w") as file:
            writer = csv.writer(file)
            writer.writerows(data)
    else:
        # Create a simple Excel file
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)

    mime = vm_const.MIME.get(file_extension.removeprefix("."))
    result = VMData.get_file_type(filepath)

    if is_empty:
        assert result != mime
    else:
        assert result == mime


def test_from_file(datafile: tuple[bool, Path], caplog: pytest.LogCaptureFixture) -> None:
    empty, filepath = datafile

    if empty:
        with pytest.raises(SystemExit):
            result = VMData.from_file(filepath, normalize=False)
            assert result is None
        assert caplog.record_tuples == [
            ("vminfo_parser.vmdata", logging.CRITICAL, "File passed in was neither a CSV nor an Excel file")
        ]
    else:
        result = VMData.from_file(filepath, normalize=False)
        assert isinstance(result, VMData)
        assert isinstance(result.df, pd.DataFrame)
        assert result.df.shape == test_const.TESTFILE_SHAPE


def test_from_file_directory(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    # Create test directory structure
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Test empty directory
    with pytest.raises(SystemExit):
        VMData.from_file(str(test_dir))
    assert "Directory included neither CSV or Excel files" in caplog.text

    # Test directory with valid files using proper column headers
    test_file = test_dir / "test.csv"
    test_file.write_text(
        "VM OS Name,VM MEM (GB),VM CPU,VM Provisioned (GB),Environment,Site Name\n" "Windows 10,8,4,100,Prod,SiteA"
    )

    # Test with normalize=False to avoid header validation
    result = VMData.from_file(str(test_dir), normalize=False)
    assert isinstance(result, VMData)


def test_from_file_invalid_type(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    # Create test file with invalid type
    test_file = tmp_path / "test.txt"
    test_file.write_text("some content")

    with pytest.raises(SystemExit):
        VMData.from_file(test_file)
    assert "File passed in was neither a CSV nor an Excel file" in caplog.text


@pytest.mark.parametrize(
    test_const.TEST_DATAFRAMES[0].keys(),
    [(pd.DataFrame(item["df"]), item["unit"], item["version"]) for item in test_const.TEST_DATAFRAMES],
    ids=[f"Version {item['version']}" for item in test_const.TEST_DATAFRAMES],
)
def test_set_column_headings(df: pd.DataFrame, unit: str, version: int) -> None:
    expected_headers = deepcopy(vm_const.COLUMN_HEADERS.get(f"VERSION_{version}").copy())

    vmdata = VMData(df=df, normalize=False)
    vmdata._set_column_headings()

    assert vmdata.column_headers == expected_headers
    assert vmdata.unit_type == unit
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
        ),
        normalize=False,
    )

    with pytest.raises(ValueError):
        vmdata._set_column_headings()

    assert vmdata.column_headers == {}


@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_set_os_columns_from_datafile(vmdata_with_headers: VMData) -> None:
    original_df = vmdata_with_headers.df.copy()
    unmodified_columns = list(set(original_df.columns).difference(set(vm_const.EXTRA_COLUMNS_DEST)))

    vmdata_with_headers._set_os_columns()

    # Validate that added columns exist
    assert all(col in vmdata_with_headers.df.columns for col in vm_const.EXTRA_COLUMNS_DEST)

    # Validate that no other columns were changed
    assert original_df[unmodified_columns].equals(vmdata_with_headers.df[unmodified_columns])


@pytest.mark.parametrize(
    "vmdata",
    [VMData(df=pd.DataFrame(item["df"]), normalize=False) for item in test_const.TEST_DATAFRAMES],
    ids=[f"Version {item['version']}" for item in test_const.TEST_DATAFRAMES],
)
def test_set_os_columns_from_df(vmdata: VMData) -> None:
    vmdata._set_column_headings()
    vmdata._set_os_columns()

    assert all(vmdata.df[vm_const.EXTRA_COLUMNS_DEST[0]].notnull())


@pytest.mark.parametrize("datafile", ["csv"], indirect=["datafile"])
def test_set_os_columns_bypass(vmdata_with_headers: VMData, caplog: pytest.LogCaptureFixture) -> None:
    vmdata_with_headers._set_os_columns()

    original_df = vmdata_with_headers.df.copy()
    vmdata_with_headers._set_os_columns()

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


@pytest.mark.parametrize(
    "env_value, prod_envs, expected",
    [
        # Test null values
        (pd.NA, ["prod"], "non-prod"),
        (None, ["prod"], "non-prod"),
        # Test empty prod_envs list
        ("any-value", [], "all envs"),
        ("prod", [], "all envs"),
        # Test prod environment matching
        ("prod", ["prod"], "prod"),
        ("production", ["prod"], "prod"),
        ("prod-env", ["prod"], "prod"),
        ("prod_environment", ["prod"], "prod"),
        # Test multiple prod environments
        ("dte", ["franklin", "dte"], "prod"),
        ("franklin", ["franklin", "dte"], "prod"),
        ("other-franklin-env", ["franklin", "dte"], "prod"),
        # Test non-prod cases
        ("dev", ["prod"], "non-prod"),
        ("staging", ["prod"], "non-prod"),
        ("test", ["prod"], "non-prod"),
        # Test case sensitivity
        ("PROD", ["prod"], "non-prod"),
        ("Prod", ["prod"], "non-prod"),
        # Test non-string input
        (123, ["prod"], "non-prod"),
        (True, ["prod"], "non-prod"),
    ],
)
def test_categorize_environment(env_value, prod_envs, expected):

    result = _categorize_environment(env_value, prod_envs)
    assert result == expected


@pytest.mark.parametrize(
    "encoding_in, content, expected_encoding",
    [
        ("utf-8", "こんにちは", "utf-8"),
        ("ISO-8859-1", "Olá Mundo", "ISO-8859-1"),
    ],
)
def test_detect_encoding(tmp_path, encoding_in, content, expected_encoding):
    """
    Create a temporary file using the provided encoding and verify that _detect_encoding
    returns the expected encoding.
    """
    file_path = tmp_path / "encoding_test.txt"
    file_path.write_text(content, encoding=encoding_in)

    detected_encoding = VMData._detect_encoding(str(file_path))
    # Normalize for case comparison
    detected_lower = detected_encoding.lower()
    expected_lower = expected_encoding.lower()

    assert detected_lower == expected_lower


@pytest.mark.parametrize(
    "delimiter, csv_content",
    [
        (",", "col1,col2\n1,2\n3,4"),
        (";", "col1;col2\n1;2\n3;4"),
        ("\t", "col1\tcol2\n1\t2\n3\t4"),
        ("|", "col1|col2\n1|2\n3|4"),
    ],
)
def test_detect_delimiter(tmp_path, delimiter, csv_content):
    file_path = tmp_path / "delimiter_test.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    detected_delimiter = VMData._detect_delimiter(str(file_path), "utf-8")
    assert detected_delimiter == delimiter


@pytest.mark.parametrize(
    "file_type,file_extensions,expected_count",
    [
        ("csv", [".csv"], 2),
        ("excel", [".xlsx"], 1),
        ("excel", [".xls", ".xlsx"], 3),
        ("text", [".txt"], 0),  # No matching files
    ],
)
def test_build_file_list(tmp_path, file_type, file_extensions, expected_count):
    # Create test files
    (tmp_path / "file1.csv").write_text("a,b\n1,2")
    (tmp_path / "file2.csv").write_text("c,d\n3,4")

    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df.to_excel(tmp_path / "file1.xlsx", index=False)
    df.to_excel(tmp_path / "file1.xls", index=False)
    df.to_excel(tmp_path / "file2.xls", index=False)

    (tmp_path / "file.txt").write_text("This is a text file")

    result = VMData.build_file_list(file_extensions, file_type, str(tmp_path))
    assert len(result) == expected_count

    if expected_count > 0:
        assert all(isinstance(df, pd.DataFrame) for df in result)


@pytest.mark.parametrize(
    "unit_type,memory_values,disk_values,expected_memory,expected_disk",
    [
        ("MiB", ["1024", "2048"], ["2048", "3072"], [1, 2], [2, 3]),
        ("MiB", [" 1024 ", " 2 048 "], [" 2048", "3 072 "], [1, 2], [2, 3]),
        ("GiB", ["1", "2"], ["2", "3"], ["1", "2"], ["2", "3"]),  # Already in GiB - expect strings
    ],
)
def test_normalize_to_GiB(unit_type, memory_values, disk_values, expected_memory, expected_disk):
    # Create a test DataFrame
    df = pd.DataFrame({"VM MEM": memory_values, "VM Disk": disk_values})

    vmdata = VMData(df.copy(), normalize=False)
    vmdata.column_headers = {"vmMemory": "VM MEM", "vmDisk": "VM Disk"}
    vmdata.unit_type = unit_type

    vmdata._normalize_to_GiB()

    # Check unit type was updated
    assert vmdata.unit_type == "GiB"

    # Check values were converted correctly, handling None values
    for i, expected in enumerate(expected_memory):
        if expected is None:
            assert pd.isna(vmdata.df["VM MEM"].iloc[i])
        else:
            assert vmdata.df["VM MEM"].iloc[i] == expected

    for i, expected in enumerate(expected_disk):
        if expected is None:
            assert pd.isna(vmdata.df["VM Disk"].iloc[i])
        else:
            assert vmdata.df["VM Disk"].iloc[i] == expected


@pytest.mark.parametrize(
    "env_values, prod_envs, env_filter, expected_count, expected_categories",
    [
        # Test with no filter - should return all rows with categorized environments
        (["prod", "dev", "test", "production"], ["prod"], None, 4, {"prod": 2, "non-prod": 2}),
        # Test with prod filter - should return only prod rows
        (["prod", "dev", "test", "production"], ["prod"], "prod", 2, {"prod": 2}),
        # Test with non-prod filter - should return only non-prod rows
        (["prod", "dev", "test", "production"], ["prod"], "non-prod", 2, {"non-prod": 2}),
        # Test with multiple prod environments
        (["dte", "dev", "frankfurt", "test"], ["dte", "frankfurt"], None, 4, {"prod": 2, "non-prod": 2}),
        # Test with "all" filter - should return all rows
        (["prod", "dev"], ["prod"], "all", 2, {"prod": 1, "non-prod": 1}),
        # Test with "both" filter - should return all rows
        (["prod", "dev"], ["prod"], "both", 2, {"prod": 1, "non-prod": 1}),
        # Test with empty DataFrame
        ([], ["prod"], None, 0, {}),
        # Test with empty prod_envs list - all should be categorized as "all envs"
        (["prod", "dev"], [], None, 2, {"all envs": 2}),
        # Test with null values in environment column
        ([None, "prod", pd.NA], ["prod"], None, 3, {"prod": 1, "non-prod": 2}),
    ],
)
def test_create_environment_filtered_dataframe(env_values, prod_envs, env_filter, expected_count, expected_categories):
    # Create a test DataFrame with environment values
    df = pd.DataFrame({"Environment": env_values, "Other Column": [1] * len(env_values)})

    # Create VMData instance
    vmdata = VMData(df.copy(), normalize=False)
    vmdata.column_headers = {"environment": "Environment"}

    # Call the method being tested
    result = vmdata.create_environment_filtered_dataframe(prod_envs=prod_envs, env_filter=env_filter)

    # Check row count
    assert len(result) == expected_count

    # Check category counts
    if expected_count > 0:
        category_counts = result["Environment"].value_counts().to_dict()
        assert category_counts == expected_categories
