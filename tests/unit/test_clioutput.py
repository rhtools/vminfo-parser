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
    "dataFrame, os_filter, expected_output",
    [
        (
            pd.DataFrame(
                {"Disk Space Range": ["0 -200 GB", "201 - 400 GB"], "non-prod": [31, 26], "prod": [247, 34]}
            ).set_index("Disk Space Range"),
            None,
            "\nDisk Space Range     non-prod    prod\n"
            "------------------  ----------  ------\n"
            "0 -200 GB               31       247\n"
            "201 - 400 GB            26        34\n\n",
        ),
        (
            pd.DataFrame({"Disk Space Range": ["0 -200 GB", "201 - 400 GB"], "Count": [278, 60]}).set_index(
                "Disk Space Range"
            ),
            None,
            "\nDisk Space Range     Count\n"
            "------------------  -------\n"
            "0 -200 GB             278\n"
            "201 - 400 GB          60\n\n",
        ),
        (
            pd.DataFrame(
                {
                    "OS Version": [7, 8, 9],
                    "Disk Space Range": ["0 -200 GB", "401 - 600 GB", "20 - 36.3 TB"],
                    "Count": [50, 52, 2],
                }
            ).set_index("OS Version"),
            "Red Hat Enterprise Linux",
            "\nRed Hat Enterprise Linux\n"
            "========================\n"
            "OS Version    Disk Space Range     Count\n"
            "------------  ------------------  -------\n"
            "7             0 -200 GB             50\n"
            "8             401 - 600 GB          52\n"
            "9             20 - 36.3 TB           2\n\n",
        ),
    ],
    ids=["split by env", "default", "split by version"],
)
def test_print_formatted_disk_space(
    cli_output: CLIOutput,
    dataFrame: pd.DataFrame,
    os_filter: str,
    expected_output: str,
) -> None:
    cli_output.print_formatted_disk_space(
        dataFrame,
        os_filter=os_filter,
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
            "\nSite Name     Memory Capacity (GB)\n"
            "-----------  ----------------------\n"
            "Site1                 533\n"
            "Site2                 764\n"
            "\nSite Name     Core Count\n"
            "-----------  ------------\n"
            "Site1            2594\n"
            "Site2            970\n"
            "\nSite Name     Disk Capacity (TB)\n"
            "-----------  --------------------\n"
            "Site1                779\n"
            "Site2                247\n"
            "\nSite Name     VM Count\n"
            "-----------  ----------\n"
            "Site1           428\n"
            "Site2           177\n\n",
        ),
    ],
    ids=["default"],
)
def test_print_site_usage(cli_output: CLIOutput, resource_list: list, df: pd.DataFrame, expected: str) -> None:
    cli_output.print_site_usage(resource_list, df)
    result = cli_output.output.getvalue()
    assert result == expected


@pytest.mark.parametrize(
    "dataFrame, headers, table_format, expected",
    [
        (
            pd.DataFrame(
                {
                    "Site Name": ["Site1", "Site2"],
                    "Site_RAM_Usage": [533, 764],
                }
            ).set_index("Site Name"),
            ["Site Name", "Memory Capacity (GB)"],
            "simple",
            "Site Name     Memory Capacity (GB)\n"
            "-----------  ----------------------\n"
            "Site1                 533\n"
            "Site2                 764",
        )
    ],
    ids=["simple"],
)
def test_create_site_table(
    cli_output: CLIOutput, dataFrame: pd.DataFrame, headers: list, table_format: str, expected: str
) -> None:
    memory_usage = dataFrame["Site_RAM_Usage"].round(0).astype(int)
    result = cli_output.create_site_table(memory_usage, headers=headers, table_format=table_format)
    assert result == expected


@pytest.mark.parametrize(
    "series, expected",
    [
        (
            pd.Series(
                [732, 280, 1100],
                index=["Microsoft Windows Server", "SUSE Linux Enterprise", "Red Hat Enterprise Linux"],
                name="Operating Systems",
            ),
            "Microsoft Windows Server     732\n"
            "SUSE Linux Enterprise        280\n"
            "Red Hat Enterprise Linux    1100\n",
        )
    ],
    ids=["default"],
)
def test_format_series_output(cli_output: CLIOutput, series: pd.Series, expected: str) -> None:
    cli_output.format_series_output(series)
    result = cli_output.output.getvalue()
    assert result == expected


@pytest.mark.parametrize(
    "dataFrame, os_name, expected",
    [
        (
            pd.DataFrame({"OS Version": ["4/5/6", "7"], "Count": [125, 600]}),
            "CentOS",
            "\nCentOS\n"
            "--------------\n"
            "OS Version			 Count\n"
            "4/5/6                            125\n"
            "7                                600\n",
        )
    ],
    ids=["default"],
)
def test_format_dataframe_output(
    cli_output: CLIOutput, dataFrame: pd.DataFrame, os_name: str | None, expected: str
) -> None:
    cli_output.format_dataframe_output(dataFrame, os_name)
    result = cli_output.output.getvalue()
    assert result == expected
