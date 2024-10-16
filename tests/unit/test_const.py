import pytest

import vminfo_parser.const as vm_const


def test_immutable_const_edit() -> None:
    with pytest.raises(TypeError):
        vm_const.COLUMN_HEADERS["test"] = "fail"


def test_immutable_const_nested() -> None:
    with pytest.raises(TypeError):
        vm_const.COLUMN_HEADERS["VERSION_1"]["test"] = "fail"


def test_immutable_frozenset() -> None:
    with pytest.raises(AttributeError):
        vm_const.MIME["excel"].add("fail")

    with pytest.raises(TypeError):
        vm_const.MIME["excel"] += set("fail")
