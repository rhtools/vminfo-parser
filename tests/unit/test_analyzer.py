from collections.abc import Generator

import pandas as pd
import pytest
from pytest_mock import MockFixture, MockType

import vminfo_parser.const as vm_const
from vminfo_parser.analyzer import Analyzer


@pytest.fixture
def analyzer(mock_config: MockType, mock_vmdata: MockType) -> Generator[Analyzer, None, None]:
    yield Analyzer(mock_vmdata, mock_config)


@pytest.mark.parametrize("os_names", [["os1"], ["os1,os2"]], ids=["single", "multiple"])
def test_by_os(analyzer: Analyzer, mocker: MockFixture, os_names: list[str]) -> None:
    test_func: MockType = mocker.MagicMock()
    mock_unique_os = mocker.patch.object(analyzer, attribute="get_unique_os_names")
    mock_unique_os.return_value = os_names

    analyzer.by_os(test_func)

    mock_unique_os.assert_called_once()
    assert test_func.call_count == len(os_names)
    test_func.assert_has_calls([((os_name,), {}) for os_name in os_names])


@pytest.mark.parametrize(
    "df_data,os_name,expected",
    [
        ({"OS Name": ["os1", "os2"]}, "os1", ["os1"]),
        ({"OS Name": ["os1", "os2"]}, None, ["os1", "os2"]),
        ({"OS Name": ["os1", "os2", ""]}, None, ["os1", "os2"]),
        ({"OS Name": ["os1", "os2", None]}, None, ["os1", "os2"]),
        ({"OS Name": ["os1", "os2"]}, "os3", []),
        ({"OS Name": ["", None]}, None, []),
    ],
    ids=[
        "os_name_filter",
        "no_os_name_filter",
        "empty_os_name_field",
        "null_os_name_field",
        "os_name_filter_not_in_data",
        "all_invalid_os_names",
    ],
)
def test_get_unique_os_names(analyzer: Analyzer, df_data: dict, os_name: str | None, expected: list[str]) -> None:
    analyzer.vm_data.df = pd.DataFrame(data=df_data)
    analyzer.config.os_name = os_name

    response = analyzer.get_unique_os_names()

    assert response == expected


def test_get_os_counts(analyzer: Analyzer, mocker: MockFixture) -> None:
    mock_df = analyzer.vm_data.create_environment_filtered_dataframe.return_value
    mock_calculate = mocker.patch.object(analyzer, "_calculate_os_counts")

    response = analyzer.get_operating_system_counts()

    analyzer.vm_data.create_environment_filtered_dataframe.assert_called_once_with(
        analyzer.config.environments, env_filter=analyzer.config.environment_filter
    )
    mock_calculate.assert_called_once_with(mock_df)

    assert response == mock_calculate.return_value


def test_get_os_counts_for_os_name(analyzer: Analyzer, mocker: MockFixture) -> None:
    mock_df: MockType = analyzer.vm_data.create_environment_filtered_dataframe.return_value
    mock_calculate: MockType = mocker.patch.object(analyzer, "_calculate_os_counts")
    analyzer.config.os_name = "os1"
    mock_filtered_df: MockType = mock_df.__getitem__.return_value

    response = analyzer.get_operating_system_counts()

    mock_df.__getitem__.assert_has_calls(
        [
            ("", ("OS Name",)),
            ("", (False,)),
        ],
        any_order=True,
    )
    mock_filtered_df.__eq__.assert_called_once_with(analyzer.config.os_name)

    analyzer.vm_data.create_environment_filtered_dataframe.assert_called_once_with(
        analyzer.config.environments, env_filter=analyzer.config.environment_filter
    )
    mock_calculate.assert_called_once_with(mock_filtered_df)

    assert response == mock_calculate.return_value


def test_get_supported_os_counts(analyzer: Analyzer, mocker: MockFixture) -> None:
    mock_calculate = mocker.patch.object(analyzer, "_calculate_os_counts")
    mock_count_df = mock_calculate.return_value
    mock_env_df = analyzer.vm_data.create_environment_filtered_dataframe.return_value
    mock_filtered_df = mock_env_df.__getitem__.return_value

    response = analyzer.get_supported_os_counts()

    # Assert create_environment_filtered_dataframe called correctly
    analyzer.vm_data.create_environment_filtered_dataframe.assert_called_once_with(
        analyzer.config.environments, env_filter=analyzer.config.environment_filter
    )

    # Assert counts filtered by supported os set from const
    mock_filtered_df.isin.assert_called_once_with(vm_const.SUPPORTED_OSES)
    mock_env_df.__getitem__.assert_has_calls(
        [
            ("", ("OS Name",), {}),
            ("", (mock_filtered_df.isin.return_value,), {}),
        ],
        any_order=True,
    )

    # Assert _calculate_os_counts called correctly
    mock_calculate.assert_called_once_with(mock_filtered_df)

    # Assert correct value is returned
    assert response == mock_count_df


def test_get_unsupported_os_counts(analyzer: Analyzer, mocker: MockFixture) -> None:
    mock_calculate = mocker.patch.object(analyzer, "_calculate_os_counts")
    mock_count_df = mock_calculate.return_value
    mock_env_df = analyzer.vm_data.create_environment_filtered_dataframe.return_value
    mock_filtered_df = mock_env_df.__getitem__.return_value

    response = analyzer.get_supported_os_counts()

    # Assert create_environment_filtered_dataframe called correctly
    analyzer.vm_data.create_environment_filtered_dataframe.assert_called_once_with(
        analyzer.config.environments, env_filter=analyzer.config.environment_filter
    )

    # Assert counts filtered by supported os set from const
    mock_filtered_df.isin.assert_called_once_with(vm_const.SUPPORTED_OSES)
    mock_env_df.__getitem__.assert_has_calls(
        [
            ("", ("OS Name",), {}),
            ("", (mock_filtered_df.isin.return_value,), {}),  # mock ignores the ~ negation that is performed by pandas
        ],
        any_order=True,
    )

    # Assert _calculate_os_counts called correctly
    mock_calculate.assert_called_once_with(mock_filtered_df)

    # Assert correct value is returned
    assert response == mock_count_df
