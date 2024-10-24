import typing as t

import pytest
from pytest_mock import MockFixture, MockType

from vminfo_parser import __main__
from vminfo_parser.analyzer import Analyzer
from vminfo_parser.clioutput import CLIOutput
from vminfo_parser.config import Config
from vminfo_parser.visualizer import Visualizer
from vminfo_parser.vmdata import VMData

from .. import const as test_const


@pytest.fixture
def mock_analyzer(mocker: MockFixture) -> t.Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(Analyzer)


@pytest.fixture
def mock_visualizer(mocker: MockFixture) -> t.Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(Visualizer)


@pytest.fixture
def mock_clioutput(mocker: MockFixture) -> t.Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(CLIOutput)


@pytest.fixture
def mock_config(mocker: MockFixture) -> t.Generator[MockType, None, None]:
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
    yield mock_config


@pytest.fixture
def mock_vmdata(mocker: MockFixture) -> t.Generator[MockType, None, None]:
    yield mocker.NonCallableMagicMock(VMData)


@pytest.fixture
def mock_main(
    mocker: MockFixture,
    mock_analyzer: MockType,
    mock_visualizer: MockType,
    mock_clioutput: MockType,
    mock_config: MockType,
    mock_vmdata: MockType,
) -> t.Generator[MockType, None, None]:
    main_obj = mocker.NonCallableMagicMock()
    main_obj.config_class = mocker.patch("vminfo_parser.__main__.Config")
    main_obj.config = main_obj.config_class.from_args.return_value = mock_config
    main_obj.vmdata_class = mocker.patch("vminfo_parser.__main__.VMData")
    main_obj.vm_data = main_obj.vmdata_class.from_file.return_value = mock_vmdata
    main_obj.visualizer_class = mocker.patch("vminfo_parser.__main__.Visualizer")
    main_obj.visualizer = main_obj.visualizer_class.return_value = mock_visualizer
    main_obj.clioutput_class = mocker.patch("vminfo_parser.__main__.CLIOutput")
    main_obj.cli_output = main_obj.clioutput_class.return_value = mock_clioutput
    main_obj.analyzer_class = mocker.patch("vminfo_parser.__main__.Analyzer")
    main_obj.analyzer = main_obj.analyzer_class.return_value = mock_analyzer
    main_obj.analyzer.cli_output = mocker.MagicMock(CLIOutput)
    main_obj.analyzer.visualizer = mocker.MagicMock(Visualizer)

    # Add main functions to mock
    for func in test_const.MAIN_FUNCTION_CALLS.keys():
        setattr(main_obj, func, mocker.patch(f"vminfo_parser.__main__.{func}"))

    yield main_obj


def test_main_default(mock_main: MockType) -> None:
    __main__.main()

    # Assert config setup
    mock_main.config_class.from_args.assert_called_once()
    mock_main.config.generate_yaml_from_parser.assert_not_called()

    # Assert vmdata setup
    mock_main.vmdata_class.from_file.assert_called_once_with(mock_main.config.file)
    mock_main.vm_data.set_column_headings.assert_called_once()
    mock_main.vm_data.add_extra_columns.assert_called_once()

    # Assert module setup
    mock_main.visualizer_class.assert_not_called()
    mock_main.clioutput_class.assert_called_once()
    mock_main.analyzer_class.assert_called_once_with(mock_main.vm_data, mock_main.config)

    # Assert main funcs not called
    mock_main.sort_by_site.assert_not_called()
    mock_main.show_disk_space_by_os.assert_not_called()
    mock_main.get_disk_space_ranges.assert_not_called()
    mock_main.get_os_counts.assert_not_called()
    mock_main.output_os_by_version.assert_not_called()
    mock_main.get_supported_os.assert_not_called()
    mock_main.get_unsupported_os.assert_not_called()

    # Assert clioutputs closed
    mock_main.cli_output.close.assert_called_once()
    mock_main.analyzer.cli_output.close.assert_called_once()


def test_main_generate_yaml(mock_main: MockType) -> None:
    mock_main.config.generate_yaml = True
    with pytest.raises(SystemExit):
        __main__.main()

    mock_main.config.generate_yaml_from_parser.assert_called_once()
    mock_main.vmdata_class.from_file.assert_not_called()


def test_main_generate_graphs(mock_main: MockType) -> None:
    mock_main.config.generate_graphs = True
    __main__.main()
    mock_main.visualizer_class.assert_called_once()


@pytest.mark.parametrize(
    ["func", "args"], test_const.MAIN_FUNCTION_CALLS.items(), ids=test_const.MAIN_FUNCTION_CALLS.keys()
)
def test_main_funcs(mock_main: MockType, func: str, args: list[str]) -> None:
    setattr(mock_main.config, func, True)
    mock_main.config.generate_graphs = True
    __main__.main()
    getattr(mock_main, func).assert_called_once_with(*[getattr(mock_main, arg) for arg in args])


def test_get_unsupported_os(mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType) -> None:
    __main__.get_unsupported_os(mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.generate_unsupported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(
        mock_analyzer.generate_unsupported_os_counts.return_value
    )
    mock_visualizer.visualize_unsupported_os_distribution.assert_called_once_with(
        mock_analyzer.generate_unsupported_os_counts.return_value
    )


def test_get_unsupported_os_no_graphs(
    mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_unsupported_os(mock_analyzer, mock_clioutput, None)
    mock_analyzer.generate_unsupported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(
        mock_analyzer.generate_unsupported_os_counts.return_value
    )
    mock_visualizer.visualize_unsupported_os_distribution.assert_not_called()



def test_sort_by_site(mock_vmdata: MockType, mock_clioutput: MockType) -> None:
    __main__.sort_by_site(mock_vmdata, mock_clioutput)
    mock_vmdata.create_site_specific_dataframe.assert_called_once()
    mock_clioutput.print_site_usage.assert_called_once_with(
        ["Memory", "CPU", "Disk", "VM"], mock_vmdata.create_site_specific_dataframe.return_value
    )
