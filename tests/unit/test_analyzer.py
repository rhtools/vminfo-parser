from collections.abc import Generator

import pandas as pd
import pytest
from pytest_mock import MockFixture, MockType

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
