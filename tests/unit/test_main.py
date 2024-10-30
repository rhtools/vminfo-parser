from collections.abc import Callable, Generator

import pytest
from pytest_mock import MockFixture, MockType

from vminfo_parser import __main__

from .. import const as test_const


@pytest.fixture
def mock_main(
    mocker: MockFixture,
    mock_analyzer: MockType,
    mock_visualizer: MockType,
    mock_clioutput: MockType,
    mock_config: MockType,
    mock_vmdata: MockType,
) -> Generator[MockType, None, None]:
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

    # Add main functions to mock
    for func in test_const.MAIN_FUNCTION_CALLS.keys():
        setattr(main_obj, func, mocker.patch(f"vminfo_parser.__main__.{func}"))

    yield main_obj


def generate_by_os_side_effect(os_names: list[str] | None) -> Callable:

    def side_effect(func: Callable[[str], None]) -> None:
        if os_names is None:
            return None
        for os_name in os_names:
            func(os_name)

    return side_effect


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


@pytest.mark.parametrize(
    ["func", "args"], test_const.MAIN_FUNCTION_CALLS.items(), ids=test_const.MAIN_FUNCTION_CALLS.keys()
)
def test_main_funcs_no_graphs(mock_main: MockType, func: str, args: list[str]) -> None:
    setattr(mock_main.config, func, True)
    expected_args: list[object | None] = []
    for arg in args:
        if arg == "visualizer":
            expected_args.append(None)
        else:
            expected_args.append(getattr(mock_main, arg))
    __main__.main()
    getattr(mock_main, func).assert_called_once_with(*expected_args)


def test_get_unsupported_os(mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType) -> None:
    __main__.get_unsupported_os(mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_unsupported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_unsupported_os_counts.return_value)
    mock_visualizer.visualize_unsupported_os_distribution.assert_called_once_with(
        mock_analyzer.get_unsupported_os_counts.return_value
    )


def test_get_unsupported_os_no_graphs(
    mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_unsupported_os(mock_analyzer, mock_clioutput, None)
    mock_analyzer.get_unsupported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_unsupported_os_counts.return_value)
    mock_visualizer.visualize_unsupported_os_distribution.assert_not_called()


def test_get_supported_os(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_supported_os(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_supported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_supported_os_counts.return_value)
    mock_visualizer.visualize_supported_os_distribution.assert_called_once_with(
        mock_analyzer.get_supported_os_counts.return_value, environment_filter=mock_config.environment_filter
    )


def test_get_supported_os_no_graphs(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_supported_os(mock_config, mock_analyzer, mock_clioutput, None)
    mock_analyzer.get_supported_os_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_supported_os_counts.return_value)
    mock_visualizer.visualize_supported_os_distribution.assert_not_called()


def test_get_os_counts(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_os_counts(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_operating_system_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_operating_system_counts.return_value)
    mock_visualizer.visualize_os_distribution.assert_called_once_with(
        mock_analyzer.get_operating_system_counts.return_value, mock_config.count_filter
    )


def test_get_os_counts_no_graphs(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    __main__.get_os_counts(mock_config, mock_analyzer, mock_clioutput, None)
    mock_analyzer.get_operating_system_counts.assert_called_once()
    mock_clioutput.format_series_output.assert_called_once_with(mock_analyzer.get_operating_system_counts.return_value)
    mock_visualizer.visualize_os_distribution.assert_not_called()


def test_sort_by_site(mock_vmdata: MockType, mock_clioutput: MockType) -> None:
    __main__.sort_by_site(mock_vmdata, mock_clioutput)
    mock_vmdata.create_site_specific_dataframe.assert_called_once()
    mock_clioutput.print_site_usage.assert_called_once_with(
        ["Memory", "CPU", "Disk", "VM"], mock_vmdata.create_site_specific_dataframe.return_value
    )


def test_show_disk_space_by_os(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.by_os.side_effect = generate_by_os_side_effect(["os1", "os2"])
    expected_df = mock_analyzer.get_disk_space.return_value
    expected_df.empty = False
    __main__.show_disk_space_by_os(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.by_os.assert_called_once()
    mock_analyzer.get_disk_space.assert_has_calls(
        [
            ((), {"os_filter": "os1"}),
            ((), {"os_filter": "os2"}),
        ]
    )
    mock_clioutput.print_formatted_disk_space.assert_has_calls(
        [
            ((expected_df,), {"os_filter": "os1"}),
            ((expected_df,), {"os_filter": "os2"}),
        ]
    )
    mock_visualizer.visualize_disk_space_vertical.assert_has_calls(
        [
            ((expected_df,), {"os_filter": "os1"}),
            ((expected_df,), {"os_filter": "os2"}),
        ]
    )
    mock_visualizer.visualize_disk_space_horizontal.assert_not_called()


def test_show_disk_space_by_os_no_graphs(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.get_unique_os_names.return_value = ["os1", "os2"]
    expected_df = mock_analyzer.get_disk_space.return_value
    expected_df.empty = False
    __main__.show_disk_space_by_os(mock_config, mock_analyzer, mock_clioutput, None)
    mock_visualizer.visualize_disk_space_vertical.assert_not_called()
    mock_visualizer.visualize_disk_space_horizontal.assert_not_called()


def test_show_disk_space_by_os_all_env(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.by_os.side_effect = generate_by_os_side_effect(["os1", "os2"])
    expected_df = mock_analyzer.get_disk_space.return_value
    expected_df.empty = False
    mock_config.environment_filter = "all"
    __main__.show_disk_space_by_os(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_visualizer.visualize_disk_space_horizontal.assert_has_calls(
        [
            ((expected_df,), {}),
            ((expected_df,), {}),
        ]
    )
    mock_visualizer.visualize_disk_space_vertical.assert_not_called()


def test_show_disk_space_by_os_empty_df(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.by_os.side_effect = generate_by_os_side_effect(["os1", "os2"])
    expected_df = mock_analyzer.get_disk_space.return_value
    expected_df.empty = True
    __main__.show_disk_space_by_os(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_clioutput.print_formatted_disk_space.assert_not_called()
    mock_visualizer.visualize_disk_space_vertical.assert_not_called()
    mock_visualizer.visualize_disk_space_horizontal.assert_not_called()


def test_output_os_by_version(mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType) -> None:
    mock_analyzer.by_os.side_effect = generate_by_os_side_effect(["os1", "os2"])
    expected_df = mock_analyzer.get_os_version_distribution.return_value
    __main__.output_os_by_version(mock_analyzer, mock_clioutput, mock_visualizer)
    mock_clioutput.format_dataframe_output.assert_has_calls(
        [
            ((expected_df,), {"os_name": "os1"}),
            ((expected_df,), {"os_name": "os2"}),
        ]
    )
    mock_visualizer.visualize_os_version_distribution.assert_has_calls(
        [
            ((expected_df,), {"os_name": "os1"}),
            ((expected_df,), {"os_name": "os2"}),
        ]
    )


def test_output_os_by_version_no_graphs(
    mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.by_os.side_effect = generate_by_os_side_effect(["os1", "os2"])
    expected_df = mock_analyzer.get_os_version_distribution.return_value
    __main__.output_os_by_version(mock_analyzer, mock_clioutput, None)
    mock_clioutput.format_dataframe_output.assert_has_calls(
        [
            ((expected_df,), {"os_name": "os1"}),
            ((expected_df,), {"os_name": "os2"}),
        ]
    )
    mock_visualizer.visualize_os_version_distribution.assert_not_called()


def test_get_disk_space_ranges(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.get_disk_space.return_value.empty = False
    __main__.get_disk_space_ranges(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_disk_space.assert_called_once_with(os_filter=mock_config.os_name)
    mock_clioutput.print_formatted_disk_space.assert_called_once_with(
        mock_analyzer.get_disk_space.return_value, os_filter=mock_config.os_name
    )
    mock_visualizer.visualize_disk_space_vertical.assert_called_once_with(
        mock_analyzer.get_disk_space.return_value, os_filter=mock_config.os_name
    )
    mock_visualizer.visualize_disk_space_horizontal.assert_not_called()


def test_get_disk_space_ranges_empty(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.get_disk_space.return_value.empty = True
    __main__.get_disk_space_ranges(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_disk_space.assert_called_once_with(os_filter=mock_config.os_name)
    mock_clioutput.print_formatted_disk_space.assert_not_called()
    mock_visualizer.visualize_disk_space_vertical.assert_not_called()
    mock_visualizer.visualize_disk_space_horizontal.assert_not_called()


def test_get_disk_space_ranges_all_env(
    mock_config: MockType, mock_analyzer: MockType, mock_clioutput: MockType, mock_visualizer: MockType
) -> None:
    mock_analyzer.get_disk_space.return_value.empty = False
    mock_config.environment_filter = "all"
    __main__.get_disk_space_ranges(mock_config, mock_analyzer, mock_clioutput, mock_visualizer)
    mock_analyzer.get_disk_space.assert_called_once_with(os_filter=mock_config.os_name)
    mock_clioutput.print_formatted_disk_space.assert_called_once_with(
        mock_analyzer.get_disk_space.return_value, os_filter=mock_config.os_name
    )
    mock_visualizer.visualize_disk_space_vertical.assert_not_called
    mock_visualizer.visualize_disk_space_horizontal.assert_called_once_with(mock_analyzer.get_disk_space.return_value)
