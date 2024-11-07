import re
from collections.abc import Generator
from pathlib import Path, PosixPath

import pytest
import yaml
from pytest_mock import MockFixture, MockType

from vminfo_parser import const as vm_const
from vminfo_parser.analyzer import Analyzer
from vminfo_parser.clioutput import CLIOutput
from vminfo_parser.config import Config
from vminfo_parser.visualizer import Visualizer
from vminfo_parser.vmdata import VMData

from .. import const as test_const


def yaml_path_representer(dumper: yaml.Dumper, path: Path) -> yaml.ScalarNode:
    return dumper.represent_str(str(path))


yaml.add_representer(PosixPath, yaml_path_representer)


@pytest.fixture(params=["csv", "xlsx", "emptycsv", "emptyxlsx"])
def datafile(tmp_path: Path, request: pytest.FixtureRequest) -> Generator[tuple[bool, Path], None, None]:
    srcfile: Path = None
    suffix: str
    if request.param.startswith("empty"):
        suffix = request.param.removeprefix("empty")
    elif "." in request.param:
        srcfile = Path(__file__).parent.parent / test_const.TESTFILE_DIR / request.param
        suffix = request.param.split(".")[-1]
    else:
        srcfile = (
            Path(__file__).parent.parent
            / test_const.TESTFILE_DIR
            / test_const.DEFAULT_TESTFILE_NAME.format(request.param)
        )
        suffix = request.param
    datafile = tmp_path / "test"
    datafile = datafile.with_suffix(f".{suffix}")
    if srcfile and srcfile.is_file():
        with open(srcfile, "rb") as src:
            with open(datafile, "wb") as dst:
                dst.writelines(src.readlines())
    else:
        datafile.touch()
    yield srcfile is None, datafile


@pytest.fixture
def vmdata(datafile: tuple[bool, Path]) -> Generator[VMData, None, None]:
    _, filepath = datafile
    yield VMData.from_file(filepath)


@pytest.fixture
def vmdata_with_headers(vmdata: VMData) -> Generator[VMData, None, None]:
    vmdata.set_column_headings()
    yield vmdata


@pytest.fixture(scope="session")
def extra_columns_regexs() -> Generator[dict[str, re.Pattern], None, None]:
    yield {
        "non_windows": re.compile(vm_const.EXTRA_COLUMNS_NON_WINDOWS_REGEX),
        "windows_server": re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX),
        "windows_desktop": re.compile(vm_const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX),
    }


@pytest.fixture
def yaml_config(tmp_path: Path, config_dict: dict) -> Generator[str, None, None]:
    yamlfile = tmp_path / "config.yaml"
    with open(yamlfile, "w") as file:
        yaml.dump(config_dict, file)
    yield str(yamlfile)


@pytest.fixture
def visualizer() -> Generator[Visualizer, None, None]:
    yield Visualizer()


@pytest.fixture
def mock_analyzer(mocker: MockFixture) -> Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(Analyzer)


@pytest.fixture
def mock_visualizer(mocker: MockFixture) -> Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(Visualizer)


@pytest.fixture
def mock_clioutput(mocker: MockFixture) -> Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(CLIOutput)


@pytest.fixture
def mock_config(mocker: MockFixture) -> Generator[MockType, None, None]:
    mock_config = mocker.NonCallableMagicMock(Config)

    # set defaults for config items
    for prop, val in [
        ("generate_yaml", False),
        ("generate_graphs", False),
        ("sort_by_site", False),
        ("show_disk_space_by_os", False),
        ("get_disk_space_ranges", False),
        ("get_os_counts", False),
        ("output_os_by_version", False),
        ("get_supported_os", False),
        ("get_unsupported_os", False),
        ("file", None),
        ("minimum_count", 0),
        ("os_name", None),
        ("over_under_tb", False),
        ("breakdown_by_terabyte", False),
        ("disk_space_by_granular_os", False),
        ("prod_env_labels", None),
        ("sort_by_env", None),
    ]:
        setattr(mock_config, prop, val)

        def environments() -> list[str]:
            if mock_config.prod_env_labels:
                return mock_config.prod_env_labels.split(",")
            return []

        mock_config.environments = mocker.PropertyMock(side_effect=environments)

        def environment_filter() -> str:
            return mock_config.sort_by_env if mock_config.sort_by_env else "all"

        mock_config.environment_filter = mocker.PropertyMock(side_effect=environment_filter)

        def count_filter() -> int | None:
            return mock_config.minimum_count if mock_config.minimum_count > 0 else None

        mock_config.count_filter = mocker.PropertyMock(side_effect=count_filter)

    yield mock_config


@pytest.fixture
def mock_vmdata(mocker: MockFixture) -> Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(VMData)
