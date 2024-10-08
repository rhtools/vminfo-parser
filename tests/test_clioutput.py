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
    print(f"result: {result}")
    print(f"expected: {expected}")

    assert result == expected
