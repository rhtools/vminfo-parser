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
):
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
):
    # There is some manipulation of the df that is required in order to mock real data
    # the index needs to be set, but the index column heading is sometimes changed for clarity
    df = df.set_index(f"{current_index_column_name}")
    result = cli_output.set_column_width(df, index_column_padding, remaining_column_padding, new_index_column_name)
    assert result == expected
