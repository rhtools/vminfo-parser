import typing as t

import pytest
from pytest_mock import MockFixture, MockType

from vminfo_parser import __main__
from vminfo_parser.analyzer import Analyzer
from vminfo_parser.clioutput import CLIOutput
from vminfo_parser.config import Config
from vminfo_parser.visualizer import Visualizer
from vminfo_parser.vmdata import VMData


@pytest.fixture
def mock_main(mocker: MockFixture) -> t.Generator[MockType, None, None]:
    main_obj = mocker.NonCallableMagicMock()
    main_obj.config_class = mocker.patch("vminfo_parser.__main__.Config", spec=Config)
    main_obj.config = main_obj.config_class.from_args.return_value

    # Disable all options by default

    main_obj.config.generate_yaml = False
    main_obj.config.generate_graphs = False
    main_obj.config.sort_by_site = False
    main_obj.config.show_disk_space_by_os = False
    main_obj.config.get_disk_space_ranges = False
    main_obj.config.get_os_counts = False
    main_obj.config.output_os_by_version = False
    main_obj.config.get_supported_os = False
    main_obj.config.get_unsupported_os = False

    main_obj.vmdata_class = mocker.patch("vminfo_parser.__main__.VMData", spec=VMData)
    main_obj.vm_data = main_obj.vmdata_class.from_file.return_value
    main_obj.visualizer_class = mocker.patch("vminfo_parser.__main__.Visualizer", spec=Visualizer)
    main_obj.visualizer = main_obj.visualizer_class.return_value
    main_obj.clioutput_class = mocker.patch("vminfo_parser.__main__.CLIOutput", spec=CLIOutput)
    main_obj.cli_output = main_obj.clioutput_class.return_value
    main_obj.analyzer_class = mocker.patch("vminfo_parser.__main__.Analyzer", spec=Analyzer)
    main_obj.analyzer = main_obj.analyzer_class.return_value
    main_obj.analyzer.cli_output = mocker.MagicMock(CLIOutput)
    main_obj.analyzer.visualizer = mocker.MagicMock(Visualizer)

    # Add main functions to mock
    for func in [
        "get_disk_space_ranges",
        "get_os_counts",
        "get_supported_os",
        "get_unsupported_os",
        "output_os_by_version",
        "show_disk_space_by_os",
        "sort_by_site",
    ]:
        setattr(main_obj, func, mocker.patch(f"vminfo_parser.__main__.{func}"))

    mocker.seal(main_obj)

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
    ["func", "args"],
    [
        ("sort_by_site", ["vm_data", "cli_output"]),
        ("show_disk_space_by_os", ["config", "vm_data", "analyzer"]),
        ("get_disk_space_ranges", ["config", "analyzer"]),
        ("get_os_counts", ["config", "analyzer"]),
        ("output_os_by_version", ["analyzer", "cli_output", "visualizer"]),
        ("get_supported_os", ["config", "analyzer", "cli_output", "visualizer"]),
        ("get_unsupported_os", ["analyzer", "cli_output", "visualizer"]),
    ],
)
def test_main_funcs(mock_main: MockType, func: str, args: list[str]) -> None:
    setattr(mock_main.config, func, True)
    mock_main.config.generate_graphs = True
    __main__.main()
    getattr(mock_main, func).assert_called_once_with(*[getattr(mock_main, arg) for arg in args])
