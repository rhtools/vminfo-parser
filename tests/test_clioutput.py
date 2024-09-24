import typing as t

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
