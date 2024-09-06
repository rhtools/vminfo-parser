import pandas as pd
import pytest

from vminfo_parser.vminfo_parser import VMData

from . import const


def test_get_file_type(datafile: tuple[str, bool, str]) -> None:
    filename = datafile[2]
    empty = datafile[1]
    mime = const.MIME.get(datafile[0])
    result = VMData.get_file_type(filename)

    if empty:
        assert result != mime
    else:
        assert result == mime


def test_from_file(
    datafile: tuple[str, bool, str], capsys: pytest.CaptureFixture
) -> None:
    filename = datafile[2]
    empty = datafile[1]

    if empty:
        with pytest.raises(SystemExit):
            result = VMData.from_file(filename)
            assert result is None
        output = capsys.readouterr()
        assert (
            output.out
            == "File passed in was neither a CSV nor an Excel file\nBailing...\n"
        )
    else:
        result = VMData.from_file(filename)
        assert isinstance(result, VMData)
        assert isinstance(result.df, pd.DataFrame)
        assert result.df.shape == const.TESTFILE_SHAPE
