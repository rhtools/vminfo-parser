import pathlib

from vminfo_parser.vminfo_parser import VMData


def test_get_file_type_csv(csv_file: str) -> None:
    result = VMData.get_file_type(csv_file)
    assert result == "text/csv"


def test_get_file_type_xlsx(xlsx_file: str) -> None:
    result = VMData.get_file_type(xlsx_file)
    assert (
        result
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_get_file_type_empty_csv(tmp_path: pathlib.Path) -> None:
    emptyfile = tmp_path / "empty.csv"
    emptyfile.touch()
    result = VMData.get_file_type(str(emptyfile))
    assert result != "text/cvs"


def test_get_file_type_empty_xlsx(tmp_path: pathlib.Path) -> None:
    emptyfile = tmp_path / "empty.xlsx"
    emptyfile.touch()
    result = VMData.get_file_type(str(emptyfile))
    assert (
        result
        != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
