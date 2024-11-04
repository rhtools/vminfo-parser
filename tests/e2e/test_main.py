import cProfile
from pathlib import Path

import pytest

from vminfo_parser.__main__ import main

from .. import const as test_const


@pytest.mark.parametrize(
    "config_dict, expected_output",
    [
        (test_const.CLI_OPTIONS[key], test_const.EXPECTED_CLI_OUTPUT[key])
        for key in test_const.EXPECTED_CLI_OUTPUT.keys()
    ],
    ids=test_const.EXPECTED_CLI_OUTPUT.keys(),
    indirect=["config_dict"],
)
def test_main_with_args(
    cli_args: list[str], expected_output: str, capsys: pytest.CaptureFixture, request: pytest.FixtureRequest
) -> None:

    outputdir = Path(__file__).parent.parent / test_const.TESTOUTPUT_DIR / request.node.nodeid
    outputdir.mkdir(parents=True, exist_ok=True)

    # Run the main function with sample arguments
    cProfile.runctx(
        statement="main(*cli_args)",
        globals={"main": main},
        locals={"cli_args": cli_args},
        filename=outputdir / "profile",
    )

    # Get the output
    output = capsys.readouterr()

    with open(outputdir / "output.txt", "w") as file:
        file.write(output.out)

    # Add your assertions here
    assert expected_output in output.out.strip()
