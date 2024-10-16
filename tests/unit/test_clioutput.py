import typing as t

import pandas as pd
import pytest

from vminfo_parser.clioutput import CLIOutput


@pytest.fixture
def cli_output() -> t.Generator[CLIOutput, None, None]:
    co = CLIOutput()
    co.output.truncate()
    yield co
    co.output.close()


@pytest.mark.parametrize("arg", ["string", "string\n", None, 0, 0.1, object()], ids=type)
def test_write(cli_output: CLIOutput, arg: t.Any) -> None:
    cli_output.write(arg)
    assert cli_output.output.getvalue() == str(arg)


@pytest.mark.parametrize("arg", ["string", "string\n", None, 0, 0.1, object()], ids=type)
def test_writeline(cli_output: CLIOutput, arg: t.Any) -> None:
    cli_output.writeline(arg)
    assert cli_output.output.getvalue() == f"{arg}" if str(arg).endswith("\n") else f"{arg}\n"


@pytest.mark.parametrize(
    "df, formatted_rows, justification, col_widths, index_column_name, expected",
    [
        (
            pd.DataFrame({"Disk Space Range": ["0 - 200 GB", "1 - 2 TB"], "non-prod": [3, 4], "prod": [5, 6]}),
            [],
            15,
            {"Disk Space Range": 22, "non-prod": 10, "prod": 10},
            "Disk Space Range",
            "0 - 200 GB                             3          5         \n"
            "1 - 2 TB                               4          6         ",
        ),
        (
            pd.DataFrame(
                {"OS Version": ["7", "9"], "Disk Space Range": ["10 - 20 TB", "801 GB - 1 TB"], "Count": [15, 26]}
            ),
            [],
            15,
            {"OS Version": 0, "Disk Space Range": 19, "Count": 19},
            "OS Version",
            "7                10 - 20 TB          15                 \n"
            "9                801 GB - 1 TB       26                 ",
        ),
    ],
)
def test_format_rows(
    cli_output: CLIOutput,
    df: pd.DataFrame,
    formatted_rows: list,
    justification: int,
    col_widths: dict,
    index_column_name: str,
    expected: str,
) -> None:
    # Depending on what is being formatted, the index of the dataframe is different
    df = df.set_index(f"{index_column_name}")
    result = cli_output.format_rows(df, formatted_rows, justification, col_widths)
    assert result == expected


@pytest.mark.parametrize(
    "df, index_column_padding, remaining_column_padding, current_index_column_name, new_index_column_name, expected",
    [
        (
            pd.DataFrame(
                pd.DataFrame({"Disk Space Range": ["0 - 200 GB", "1 - 2 TB"], "non-prod": [3, 4], "prod": [5, 6]})
            ),
            22,
            10,
            "Disk Space Range",
            "Environment",
            {"Environment": 22, "non-prod": 10, "prod": 10},
        ),
        (
            pd.DataFrame(
                {"OS Version": ["7", "9"], "Disk Space Range": ["10 - 20 TB", "801 GB - 1 TB"], "Count": [15, 26]}
            ),
            0,
            19,
            "OS Version",
            "OS Version Number",
            {"OS Version Number": 0, "Disk Space Range": 19, "Count": 19},
        ),
        (
            pd.DataFrame({"Disk Space Range": ["20 - 50 TB", "801 GB - 1 TB"], "Count": [335, 2006]}),
            17,
            17,
            "Disk Space Range",
            None,
            {"Count": 17},
        ),
    ],
)
def test_set_column_width(
    cli_output: CLIOutput,
    df: pd.DataFrame,
    index_column_padding: int,
    remaining_column_padding: int,
    current_index_column_name: str,
    new_index_column_name: str,
    expected: dict,
) -> None:
    # There is some manipulation of the df that is required in order to mock real data
    # the index needs to be set, but the index column heading is sometimes changed for clarity
    df = df.set_index(f"{current_index_column_name}")
    result = cli_output.set_column_width(df, index_column_padding, remaining_column_padding, new_index_column_name)
    assert result == expected


@pytest.mark.parametrize(
    "col_widths, formatted_df_str, os_filter, display_header, index_heading_justification, "
    "other_headings_justification, expected_output",
    [
        (
            {"Environment": 22, "non-prod": 10, "prod": 10},
            "0 - 200 GB                             31         247       "
            "201 - 400 GB                           26         34        ",
            None,
            True,
            39,
            11,
            "Environment                            non-prod   prod       \n"
            "0 - 200 GB                             31         247       "
            "201 - 400 GB                           26         34        \n\n",
        ),
        (
            {"Count": 17},
            "Disk Space Range    Count            \n"
            "0 - 200 GB          278              \n"
            "201 - 400 GB        60               ",
            None,
            True,
            39,
            11,
            "\nDisk Space Range    Count            \n"
            "0 - 200 GB          278              \n"
            "201 - 400 GB        60               \n\n",
        ),
        (
            {"OS Version Number": 0, "Disk Space Range": 19, "Count": 19},
            "7                        0 - 200 GB          50                 \n"
            "8                        401 - 600 GB        52                 \n"
            "9                        20 - 36.3 TB        2                  ",
            "Red Hat Enterprise Linux",
            True,
            25,
            20,
            "Red Hat Enterprise Linux\n"
            "---------------------------------\n"
            "OS Version Number        Disk Space Range    Count               \n"
            "7                        0 - 200 GB          50                 \n"
            "8                        401 - 600 GB        52                 \n"
            "9                        20 - 36.3 TB        2                  \n\n",
        ),
    ],
)
def test_print_formatted_disk_space(
    cli_output: CLIOutput,
    col_widths: dict,
    formatted_df_str: str,
    os_filter: str,
    display_header: bool,
    index_heading_justification: int,
    other_headings_justification: int,
    expected_output: str,
) -> None:
    cli_output.print_formatted_disk_space(
        col_widths,
        formatted_df_str,
        os_filter=os_filter,
        display_header=display_header,
        index_heading_justification=index_heading_justification,
        other_headings_justification=other_headings_justification,
    )
    result = cli_output.output.getvalue()
    assert result == expected_output


@pytest.mark.parametrize(
    "resource_list, df, expected",
    [
        (
            ["Memory", "CPU", "Disk", "VM"],
            pd.DataFrame(
                {
                    "Site Name": ["Site1", "Site2"],
                    "Site_RAM_Usage": [533, 764],
                    "Site_Disk_Usage": [779, 247],
                    "Site_CPU_Usage": [2594, 970],
                    "Site_VM_Count": [428, 177],
                }
            ),
            "Site Wide Memory Usage\n"
            "-------------------\n"
            "Site1		533 GB\n"
            "Site2		764 GB\n\n"
            "Site Wide CPU Usage\n"
            "-------------------\n"
            "Site1		2594 Cores\n"
            "Site2		970 Cores\n\n"
            "Site Wide Disk Usage\n"
            "-------------------\n"
            "Site1		779 TB\n"
            "Site2		247 TB\n\n"
            "Site Wide VM Usage\n"
            "-------------------\n"
            "Site1		428 VMs\n"
            "Site2		177 VMs\n\n",
        ),
    ],
)
def test_print_site_usage(cli_output: CLIOutput, resource_list: list, df: pd.DataFrame, expected) -> None:
    cli_output.print_site_usage(resource_list, df)
    result = cli_output.output.getvalue()
    assert result == expected
